from pydantic import BaseModel

class UserRequest(BaseModel):
    data: str   
    user: str
