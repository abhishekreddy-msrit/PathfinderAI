Pathfinder AI

A Learning Companion to organize, track, and improve your learning journey.

Tech Stack

-Backend: Python, FastAPI
-Database: MongoDB Atlas
-Authentication: Session-based (Bcrypt + Secure Cookies)

How to Run Locally

1. Clone the repo

git clone [https://github.com/abhishekreddy-msrit/PathfinderAI.git](https://github.com/abhishekreddy-msrit/PathfinderAI.git)


2. Create and Activate Virtual Environment

python -m venv .venv
.\.venv\Scripts\activate


3. Install Dependencies

pip install -r requirements.txt


4. Run the Server

uvicorn main:app --reload


5. Access the API Dashboard

Once the server is running, click here: http://127.0.0.1:8000/docs

Use this page to register, login, and manage subjects.