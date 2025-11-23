from fastapi import FastAPI, HTTPException, Request
from pymongo import MongoClient
from starlette.middleware.sessions import SessionMiddleware 

# IMPORTANT: We import ALL the models we need, including the new Subject ones
from models import UserCreate, UserResponse, SubjectCreate, SubjectResponse 
import auth

app = FastAPI()

# --- SECURITY SETTINGS ---
# This adds the "Wristband" system. 
# "secret_key" should be a random string. It signs the cookies so users can't fake them.
app.add_middleware(SessionMiddleware, secret_key="MY_SUPER_SECRET_KEY")

# --- DATABASE CONNECTION ---
# 🚨 Ensure this string has your REAL password (no < > symbols)
CONNECTION_STRING = "mongodb+srv://cherry1024_db_user:pathfinder123@pathfindercluster.otvy0yu.mongodb.net/?appName=PathfinderCluster"

try:
    client = MongoClient(CONNECTION_STRING)
    db = client['pathfinderDB']
    users_collection = db['users']
    subjects_collection = db['subjects'] # We added this collection for Stage 4
    print("✅ Connected to MongoDB!")
except Exception as e:
    print(f"❌ Connection failed: {e}")

@app.get("/")
def read_root():
    return {"message": "PathfinderAI Backend is Running!"}

# --- REGISTRATION ---
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate):
    # 1. Check if email already exists
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Hash password
    hashed_pass = auth.hash_password(user.password)
    
    # 3. Create user dict
    user_dict = {"email": user.email, "full_name": user.full_name, "password": hashed_pass}
    
    # 4. Save to DB
    result = users_collection.insert_one(user_dict)
    
    # 5. Return success
    return {"_id": str(result.inserted_id), "email": user.email, "full_name": user.full_name}

# --- LOGIN ---
@app.post("/login")
def login_user(request: Request, email: str, password: str):
    # 1. Find the user
    user = users_collection.find_one({"email": email})
    
    # 2. Check if user exists AND if password matches
    if not user or not auth.verify_password(password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # 3. Create Session (The Wristband)
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

# --- CREATE SUBJECT (Stage 4 Feature) ---
@app.post("/subjects", response_model=SubjectResponse)
def create_subject(subject: SubjectCreate, request: Request):
    # 1. Check if user is logged in
    user_email = request.session.get('user_email')
    if not user_email:
        raise HTTPException(status_code=401, detail="You must be logged in to create subjects.")

    # 2. Find the User's ID (to link the subject to them)
    user = users_collection.find_one({"email": user_email})
    
    # 3. Create the Subject Data
    subject_dict = {
        "name": subject.name,
        "description": subject.description,
        "owner_id": str(user["_id"]) # This links the subject to the logged-in user
    }

    # 4. Save to MongoDB
    result = subjects_collection.insert_one(subject_dict)

    # 5. Return the result
    return {
        "_id": str(result.inserted_id),
        "name": subject.name,
        "description": subject.description,
        "owner_id": str(user["_id"])
    }

# --- GET MY SUBJECTS (Stage 4 Feature) ---
@app.get("/subjects", response_model=list[SubjectResponse])
def get_my_subjects(request: Request):
    # 1. Check login
    user_email = request.session.get('user_email')
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # 2. Find the User
    user = users_collection.find_one({"email": user_email})

    # 3. Find ONLY subjects that belong to this user
    my_subjects = list(subjects_collection.find({"owner_id": str(user["_id"])}))

    # 4. Convert _id to string for every subject found so Pydantic is happy
    for sub in my_subjects:
        sub["_id"] = str(sub["_id"])
        
    return my_subjects