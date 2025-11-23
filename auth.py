# auth.py
import bcrypt

# Function to Hash a password (used during Registration)
def hash_password(password: str) -> str:
    # 1. Generate a random "salt" (random noise)
    salt = bcrypt.gensalt()
    # 2. Scramble the password with the salt
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    # 3. Return it as a string so we can save it in the database
    return hashed_bytes.decode('utf-8')

# Function to Verify a password (used during Login)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )