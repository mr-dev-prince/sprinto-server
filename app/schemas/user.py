from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email:EmailStr
    name:str