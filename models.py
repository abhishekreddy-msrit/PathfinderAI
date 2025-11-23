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


# --- SUBJECT MODELS ---

# 1. SubjectCreate: What the user sends to create a subject
class SubjectCreate(BaseModel):
    name: str
    description: str = None # Optional field

# 2. SubjectResponse: What we send back
class SubjectResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: str = None
    owner_id: str # We will return the ID of the user who owns it

    class Config:
        populate_by_name = True