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
def ask_assistant(input: str) -> str:
    """
    Ask the AI assistant the input query and return the response.

    Args:
        input (str): The query to ask the AI.

    Returns:
        str: The response from the AI.
    """
    if not input:
        return ""
    try:
        # Add the user message to the chat history
        chat_history.add_user_message(input)

        # Construct the system message with tools and memory
        tools_message = "\n".join(f"- {tool}" for tool in tools)
        system_message = f"{prompt_raw}\n{tools_message}\n{memory.buffer}"

        # Call the Azure OpenAI chat API
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": input},
            ]
        )
        # Get the AI response and add it to the chat history
        ai_response = response.choices[0].message.content
        chat_history.add_ai_message(ai_response)

        return ai_response

    except Exception as e:
        # Return the error message if there's an exception
        return str(e)
