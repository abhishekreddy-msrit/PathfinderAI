from fastapi import FastAPI, HTTPException, Request # <--- Added Request
from pymongo import MongoClient
# --- NEW IMPORT ---
from starlette.middleware.sessions import SessionMiddleware 

from models import UserCreate, UserResponse
import auth

app = FastAPI()

# --- ADD THIS BLOCK: SECURITY SETTINGS ---
# This adds the "Wristband" system. 
# "secret_key" should be a random string. It signs the cookies so users can't fake them.
app.add_middleware(SessionMiddleware, secret_key="MY_SUPER_SECRET_KEY")

# --- DATABASE CONNECTION ---
# (Keep your existing connection string here!)
CONNECTION_STRING = "mongodb+srv://cherry1024_db_user:pathfinder123@pathfindercluster.otvy0yu.mongodb.net/?appName=PathfinderCluster"

try:
    client = MongoClient(CONNECTION_STRING)
    db = client['pathfinderDB']
    users_collection = db['users']
    print("✅ Connected to MongoDB!")
except Exception as e:
    print(f"❌ Connection failed: {e}")

@app.get("/")
def read_root():
    return {"message": "PathfinderAI Backend is Running!"}

# --- REGISTRATION (Keep this as is) ---
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate):
    # ... (Your existing registration code stays here) ...
    # (Just copying it here for reference, don't delete your existing code!)
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pass = auth.hash_password(user.password)
    user_dict = {"email": user.email, "full_name": user.full_name, "password": hashed_pass}
    result = users_collection.insert_one(user_dict)
    return {"_id": str(result.inserted_id), "email": user.email, "full_name": user.full_name}

# --- NEW: LOGIN ENDPOINT ---
@app.post("/login")
def login_user(request: Request, email: str, password: str):
    # 1. Find the user
    user = users_collection.find_one({"email": email})
    
    # 2. Check if user exists AND if password matches
    if not user or not auth.verify_password(password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # 3. Create Session (The Wristband)
    # We store the user's email in the session to remember them.
    request.session['user_email'] = user['email']
    
    return {"message": f"Welcome back, {user['full_name']}! You are logged in."}

# --- NEW: LOGOUT ENDPOINT ---
@app.post("/logout")
def logout_user(request: Request):
    # Clear the session
    request.session.clear()
    return {"message": "Logged out successfully"}

# --- NEW: CHECK SESSION (To prove it works) ---
@app.get("/whoami")
def get_current_user(request: Request):
    user_email = request.session.get('user_email')
    if not user_email:
        return {"message": "You are not logged in."}
    return {"message": f"You are currently logged in as {user_email}"}