import os
import csv
from dotenv import load_dotenv
from openai import AzureOpenAI
from src.services.prompt import prompt_raw
from src.services.tools.build_tools import tools
from src.schemas.manager_info import select_manager
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
load_dotenv()
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2023-12-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
chat_history = ChatMessageHistory()
memory = ConversationBufferMemory(chat_memory=chat_history)
def ask_assistant( input: str)->str:
       try:
        chat_history.add_user_message(input)

        tools_message = "\n".join(f"- {tool}" for tool in tools)


        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": prompt_raw},
                {"role": "user", "content": input},
                {"role": "system", "content": tools_message},
                {"role": "system", "content": memory.buffer}
                
            ]
        )
        clara_ai_resp = response.choices[0].message.content
        chat_history.add_ai_message(clara_ai_resp)

       except Exception as e:
        return str(e)

       return clara_ai_resp
