from langchain.agents import tool
from src.schemas.manager_info import select_manager

@tool
def get_manager(txt: str) -> str:
    """
    Use this tool when you collect the information to create an account from the users and assign them dynamically
    to managers based on the workload, performance rating, industry experience, client satisfaction score and location.
    """
    best_manager = select_manager()
    return str(best_manager)
