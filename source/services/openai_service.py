# services/openai_service.py

import os
import openai
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
import tiktoken
client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)   

class OpenAIService:
    def __init__(self):
        self.messages = []
        # Inicializar el cliente de ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./chroma")
        # Acceder a la colección
        self.collection = self.chroma_client.get_or_create_collection(name="my_collection")


    def add_message(self, role, content):
        self.messages.append({'role': role, 'content': content})


    def retrieve_relevant_info(self, user_input, top_k=3):
        # Generar el embedding del mensaje del usuario
        embedding_response = client.embeddings.create(
            input=user_input,
            model="text-embedding-ada-002"
        )
        query_embedding = embedding_response['data'][0]['embedding']

        # Realizar la consulta en ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents']
        )

        # Extraer los documentos recuperados
        documents = results.get('documents', [[]])[0]

        # Combinar los documentos en una sola cadena de texto
        context = "\n\n".join(documents)

        # Opcional: limitar la longitud del contexto
        max_context_length = 1500  # Ajusta este valor según sea necesario
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."

        return context

    def get_response(self):
        user_message = self.messages[-1]['content']
        print(f"User: {user_message}")

        # Recuperar información relevante de ChromaDB
        context = self.retrieve_relevant_info(user_message)

         # Construir los mensajes para enviar a OpenAI
        messages = []

        # Agregar contexto como mensaje del sistema
        if context:
            messages.append({
                'role': 'system',
                'content': f"Información de contexto relevante:\n{context}"
            })

        # Agregar el historial de mensajes
        messages.extend(self.messages)

        response = client.chat.completions.create(
            model='gpt-3.5-turbo',  # Specify the model
            messages=[
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,  # Adjust token count as needed
            temperature=0.1  # Adjust temperature for variability
        )
        
        assistant_message = response.choices[0].message.content  # Access the generated message content
        print(f"ChatGTP: {response.choices[0].message.content}")

        self.add_message('assistant', assistant_message)
        return assistant_message