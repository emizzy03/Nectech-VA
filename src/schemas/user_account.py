from pydantic import BaseModel

class Create_Account (BaseModel):
    name: str
    email: str
    CompanyAddress: str
    phone: int


def info(account: Create_Account) -> str:
    """
    Return a string with the relevant information from the Create_Account object.
    """
    return (
        f"Name: {account.name}, "
        f"Email: {account.email}, "
        f"Company Address: {account.CompanyAddress}, "
        f"Phone: {account.phone}"
    )
