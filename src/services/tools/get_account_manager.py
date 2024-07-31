from langchain.agents import tool
from src.schemas.manager_info import select_manager

@tool()
def get_managers(txt: str) -> str:
    """
    Use this tool when you collect the information to create an account from the users and assign them dynamically 
    to managers based on the workload, performance rating, industry experience, and client satisfaction score.
    """
    manager = select_manager()
    return str(manager)