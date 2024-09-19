# Importaciones necesarias
from abc import ABC, abstractmethod
import os
import PyPDF2
import pandas as pd
from docx import Document
from odf.opendocument import load
from odf.text import P
from openai import OpenAI
from pymilvus import model

# Implementaciones de FileProcessor y los procesadores concretos
from abc import ABC, abstractmethod
import tiktoken
client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
) 

class FileProcessor(ABC):
    @abstractmethod
    def process(self, file_path):
        pass


class PDFProcessor(FileProcessor):
    def process(self, file_path):
        text = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

class ExcelProcessor(FileProcessor):
    def process(self, file_path):
        text = ""
        excel_file = pd.ExcelFile(file_path)
        for sheet_name in excel_file.sheet_names:
            df = excel_file.parse(sheet_name)
            text += df.to_string(index=False, header=False) + "\n"
        return text

class WordProcessor(FileProcessor):
    def process(self, file_path):
        text = ""
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text

class ODTProcessor(FileProcessor):
    def process(self, file_path):
        text = ""
        doc = load(file_path)
        all_paragraphs = doc.getElementsByType(P)
        for para in all_paragraphs:
            for node in para.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    text += node.data + "\n"
        return text


class FileProcessorFactory:
    _processors = {
        ".pdf": PDFProcessor(),
        ".xlsx": ExcelProcessor(),
        ".xls": ExcelProcessor(),
        ".docx": WordProcessor(),
        ".odt": ODTProcessor(),
    }

    @classmethod
    def get_processor(cls, file_extension):
        processor = cls._processors.get(file_extension.lower())
        if not processor:
            raise ValueError(f"No hay procesador para la extensión {file_extension}")
        return processor


class Vectorizer:
    def __init__(self, chroma_client):
        self.chroma_client = chroma_client
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.max_tokens = 8192  # Límite de tokens para el modelo text-embedding-ada-002

    def vectorize(self, text):
        openai_ef = model.dense.OpenAIEmbeddingFunction(
            model_name="text-embedding-ada-002",
            dimensions=512
        )
        segments = self.split_text(text)
        collection = self.chroma_client.get_collection(name="my_collection")
        

        for idx, segment in enumerate(segments):
            # Generar el embedding usando el método actualizado
            response = client.embeddings.create(
                input=segment,
                model="text-embedding-ada-002",
            )
            embedding = response.data[0].embedding

            print(f"idx: {idx+1}")

            # Almacenar el embedding en ChromaDB
            collection.add(
                ids=[f"doc_{idx}"],
                documents=[segment],
                embeddings=[embedding]
            )
            results = collection.query(
                query_texts=["What is the student name?"],
                n_results=1
            )

            print(f"resultados: {results}")
            #print(f"Segmento {idx+1} almacenado en ChromaDB")




    def split_text(self, text):
        tokens = self.tokenizer.encode(text)
        segments = []
        for i in range(0, len(tokens), self.max_tokens):
            segment_tokens = tokens[i : i + self.max_tokens]
            segment_text = self.tokenizer.decode(segment_tokens)
            segments.append(segment_text)
        return segments


class FileVectorizationModule:
    def __init__(self, chroma_client):
        self.vectorizer = Vectorizer(chroma_client)

    def process_file(self, file_path):
        _, ext = os.path.splitext(file_path)
        print(f"archivo: {file_path}")
        processor = FileProcessorFactory.get_processor(ext)
        text = processor.process(file_path)
        self.vectorizer.vectorize(text)
