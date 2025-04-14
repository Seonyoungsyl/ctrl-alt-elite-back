from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext

app = FastAPI()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.user_db

# Models
class UserSignup(BaseModel):
    accountType: str
    fullName: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# Helper functions
def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Routes
@app.post("/signup")
async def signup(user: UserSignup):
    # Checking if user already exists
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user with hashed password
    user_dict = user.model_dump()
    user_dict["password"] = get_password_hash(user_dict["password"])
    result = await db.users.insert_one(user_dict)
    
    return {"message": "User created successfully", "id": str(result.inserted_id)}

@app.post("/login")
async def login(user: UserLogin):
    # Finding user
    db_user = await db.users.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    return {"message": "Login successful", "user": {
        "id": str(db_user["_id"]),
        "accountType": db_user["accountType"],
        "fullName": db_user["fullName"],
        "email": db_user["email"]
    }}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 