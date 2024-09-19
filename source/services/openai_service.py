# services/openai_service.py

import os
import openai
from openai import OpenAI

openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAIService:
    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        self.messages.append({'role': role, 'content': content})

    def get_response(self):
        user_message = self.messages[-1]['content']
        print(f"User: {user_message}")
        client = OpenAI()
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',  # Specify the model
            messages=[
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,  # Adjust token count as needed
            temperature=0.1  # Adjust temperature for variability
        )
        print(f"ChatGTP: {response.choices[0].message.content}")
        
        assistant_message = response.choices[0].message.content  # Access the generated message content
    
        self.add_message('assistant', assistant_message)
        return assistant_message