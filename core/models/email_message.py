from pydantic import BaseModel

class EmailMessage(BaseModel):
    subject: str
    body: str
    sender: str