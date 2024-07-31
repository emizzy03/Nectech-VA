from pydantic import BaseModel

class Create_Account (BaseModel):
    name: str
    email: str
    CompanyAddress: str
    phone: int


def info(body: Create_Account):
    name = body.name
    email = body.email
    company_address = body.CompanyAddress
    phone = body.phone

    return f"Name: {name}, Email: {email}, Company Address: {company_address}, Phone: {phone}"