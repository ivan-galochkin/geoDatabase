from pydantic import BaseModel


class UserPd(BaseModel):
    email: str
    password: str


