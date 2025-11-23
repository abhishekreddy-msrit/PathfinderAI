# models.py
from pydantic import BaseModel, EmailStr, Field

# 1. UserCreate: What the user sends us to Register
# Pydantic will auto-reject requests if 'email' is not a valid email format.
class UserCreate(BaseModel):
    email: EmailStr  
    password: str
    full_name: str

# 2. UserResponse: What we send BACK to the user
# We create a separate model because we MUST NOT return the password.
class UserResponse(BaseModel):
    id: str = Field(alias="_id") # Renames MongoDB's '_id' to just 'id'
    email: EmailStr
    full_name: str
    
    # This config allows Pydantic to read data by either name
    class Config:
        populate_by_name = True