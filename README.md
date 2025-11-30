Pathfinder AI

A Learning Companion to organize, track, and improve your learning journey.

Project Status (Stage 1-5 Complete)

The core authentication, subject management, and frontend integration phases are complete and stable.

Backend: Full CRUD (Create, Read, Update, Delete) implemented for Subjects.

Authentication: Session-based Login/Logout is fully working and persistent (7-day cookie).

Integration: Frontend (HTML/JS) and Backend (FastAPI) are successfully synced (CORS/Credentials configured).

Tech Stack

Backend: Python, FastAPI

Database: MongoDB Atlas

Authentication: Session-based (Bcrypt + Secure Cookies)

🚀 Getting Started

1. Setup & Run Server

Command

Purpose

git clone [REPO URL]

Download the project.

python -m venv .venv

Create your isolated toolbox.

.\.venv\Scripts\activate

Activate the toolbox (Mandatory for every session).

pip install -r requirements.txt

Install all necessary dependencies.

uvicorn main:app --reload

Start the web server.

2. How to Access and Test

Once the server is running, you can access the application through two methods:

A. Frontend User Interface (Full CRUD)

Open your browser to: http://127.0.0.1:5500/login.html (or http://localhost:5500/login.html).

Action: Log in with a registered email.

CRUD Operations: You can immediately create, delete, and edit subjects directly on the dashboard.

B. API Tester / Backend Documentation

Open your browser to: http://127.0.0.1:8000/docs

Access: This page allows you to manually test every endpoint (/register, /login, /subjects) and see the raw JSON responses.
