from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: constr(min_length=8, max_length=72)
        
class UserInDB(UserBase):
    id: str
    created_at: datetime
    is_active: bool
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    email: Optional[str] = None