from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List
from bson import ObjectId
import os
from dotenv import load_dotenv
from models import Profile

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.user_db

profile_router = APIRouter()

# update user profile with mentor_name and fun_facts
@profile_router.post("/profile/{email}")
async def update_profile(profile: Profile, email: str):
    # find user from users collection by email
    db_user = await db.users.find_one({"email": email})

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # update info of profile with given email in the database (set val of mentor_name and fun_facts)
    update = await db.users.update_one(
        {"email": email},
        {"$set": {"mentor_name": profile.mentor_name, "fun_facts": profile.fun_facts}}
    )

    return {"message": "Profile updated successfully"}


# fetch user's profile info (name, email, role, mentor_name, fun_facts, points)
@profile_router.get("/profile/{email}")
async def get_profile(email: str) -> Profile:
    # find user from users collection by email
    db_user = await db.users.find_one({"email": email})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # return profile as instance of the Profile model
    return Profile(
        fullName=db_user["fullName"],
        email=db_user["email"],
        role=db_user["accountType"],
        mentor_name=db_user.get("mentor_name", "n/a"),
        fun_facts=db_user.get("fun_facts", "n/a"),
        points=db_user.get("points", 0)
    )