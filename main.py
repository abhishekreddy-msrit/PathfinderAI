from fastapi import FastAPI, HTTPException, Request
from pymongo import MongoClient
from starlette.middleware.sessions import SessionMiddleware 
from fastapi.middleware.cors import CORSMiddleware # <--- Ensure this is imported
from bson import ObjectId # <--- This is needed for ObjectId(subject_id)

from models import UserCreate, UserResponse, SubjectCreate, SubjectResponse 
import auth

app = FastAPI()

# --- SECURITY SETTINGS ---

# 1. CORS (The "Bridge" for your Frontend)
# CRITICAL FIX: Explicitly allow your frontend URL.
# Wildcards ["*"] DO NOT work with cookies/credentials.
app.add_middleware(
    CORSMiddleware,
    # This list must contain the exact URL shown in your browser address bar
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# 2. SESSIONS (The "Wristband" for Login)
app.add_middleware(
    SessionMiddleware, 
    secret_key="MY_SUPER_SECRET_KEY", 
    max_age=604800,      # 7 Days
    same_site="lax",     # Allow cookies on same domain
    https_only=False     # Allow cookies over HTTP
)

# --- DATABASE CONNECTION ---
# 🚨 Ensure this string has your REAL password
CONNECTION_STRING = "mongodb+srv://cherry1024_db_user:pathfinder123@pathfindercluster.otvy0yu.mongodb.net/?appName=PathfinderCluster"

try:
    client = MongoClient(CONNECTION_STRING)
    db = client['pathfinderDB']
    users_collection = db['users']
    subjects_collection = db['subjects']
    print("✅ Connected to MongoDB!")
except Exception as e:
    print(f"❌ Connection failed: {e}")

@app.get("/")
def read_root():
    return {"message": "PathfinderAI Backend is Running!"}

# --- REGISTRATION ---
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pass = auth.hash_password(user.password)
    user_dict = {"email": user.email, "full_name": user.full_name, "password": hashed_pass}
    result = users_collection.insert_one(user_dict)
    
    return {"_id": str(result.inserted_id), "email": user.email, "full_name": user.full_name}

# --- LOGIN ---
@app.post("/login")
def login_user(request: Request, email: str, password: str):
    user = users_collection.find_one({"email": email})
    
    if not user or not auth.verify_password(password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    request.session['user_email'] = user['email']
    
    return {"message": f"Welcome back, {user['full_name']}! You are logged in."}

# --- LOGOUT ---
@app.post("/logout")
def logout_user(request: Request):
    request.session.clear()
    return {"message": "Logged out successfully"}

# --- CHECK SESSION ---
@app.get("/whoami")
def get_current_user(request: Request):
    user_email = request.session.get('user_email')
    if not user_email:
        return {"message": "You are not logged in."}
    return {"message": f"You are currently logged in as {user_email}"}

# --- CREATE SUBJECT ---
@app.post("/subjects", response_model=SubjectResponse)
def create_subject(subject: SubjectCreate, request: Request):
    user_email = request.session.get('user_email')
    if not user_email:
        raise HTTPException(status_code=401, detail="You must be logged in to create subjects.")

    user = users_collection.find_one({"email": user_email})
    
    subject_dict = {
        "name": subject.name,
        "description": subject.description,
        "owner_id": str(user["_id"]) 
    }

    result = subjects_collection.insert_one(subject_dict)

    return {
        "_id": str(result.inserted_id),
        "name": subject.name,
        "description": subject.description,
        "owner_id": str(user["_id"])
    }

# --- GET MY SUBJECTS ---
@app.get("/subjects", response_model=list[SubjectResponse])
def get_my_subjects(request: Request):
    user_email = request.session.get('user_email')
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = users_collection.find_one({"email": user_email})
    my_subjects = list(subjects_collection.find({"owner_id": str(user["_id"])}))

    for sub in my_subjects:
        sub["_id"] = str(sub["_id"])
        
    return my_subjects


# main.py (ADD THIS TO THE BOTTOM)

# --- DELETE SUBJECT ---
@app.delete("/subjects/{subject_id}")
def delete_subject(subject_id: str, request: Request):
    user_email = request.session.get('user_email')
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = users_collection.find_one({"email": user_email})

    # CRITICAL: Delete only if the subject ID AND owner ID match
    delete_result = subjects_collection.delete_one({
        "_id": ObjectId(subject_id),
        "owner_id": str(user["_id"])
    })

    if delete_result.deleted_count == 1:
        return {"message": "Subject deleted successfully"}

    raise HTTPException(status_code=404, detail="Subject not found or you don't own it.")


# main.py (REPLACE THE EXISTING update_subject FUNCTION)

# --- UPDATE SUBJECT (Using PUT) ---
@app.put("/subjects/{subject_id}", response_model=SubjectResponse)
def update_subject(subject_id: str, subject: SubjectCreate, request: Request):
    user_email = request.session.get('user_email')
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = users_collection.find_one({"email": user_email})

    # 1. Update Payload
    update_data = {
        "name": subject.name,
        "description": subject.description
    }
    
    # 2. Check if subject exists first (improves error handling)
    if not subjects_collection.find_one({"_id": ObjectId(subject_id)}):
         raise HTTPException(status_code=404, detail="Subject not found.")

    # 3. Perform Update (CRITICAL: ensure owner_id matches)
    # The filter ensures only the correct owner can update the document
    update_result = subjects_collection.update_one(
        {"_id": ObjectId(subject_id), "owner_id": str(user["_id"])},
        {"$set": update_data}
    )

    if update_result.modified_count == 1:
        # Fetch the updated document
        updated_subject = subjects_collection.find_one({"_id": ObjectId(subject_id)})
        
        # Manually convert the MongoDB ObjectId to a string for the response model
        updated_subject['_id'] = str(updated_subject['_id'])
        
        return updated_subject

    # 4. Handle cases where the subject wasn't found or wasn't updated by the current user
    raise HTTPException(status_code=404, detail="Subject not found or you don't own it.")