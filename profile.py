from fastapi import FastAPI, APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List
from bson import ObjectId
import os
from dotenv import load_dotenv
from models import Profile, ProfileOut, UpdateProfile
from database import db
from pymongo import ReturnDocument

profile_router = APIRouter()

users_collection = db["profiles"]

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

#---------------------------------------------------------------------------------------------------
# -----IMPORTANT: There are duplicate get requests for /profile/{email}, someone pls fix this ------
#---------------------------------------------------------------------------------------------------

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

#----------------------------------------------------------------------------
# -----IMPORTANT: update_profile is defined twice, someone pls fix this -----
#----------------------------------------------------------------------------


# GET PROFILE INFO ABOUT USER
@profile_router.get("/profile/{email}", response_model=ProfileOut)

async def update_profile(email:str):
    user = await users_collection.find_one({"email":email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["_id"] = str(user["_id"])
    return user

# UPDATE USER INFORMATION
@profile_router.put("/profile/{email}", response_model=Profile)
async def update_profile(email:str, update:UpdateProfile = Body(...)):
    # create dictionary with only fields that aren't None
    update = {
        k: v for k, v in update.model_dump(by_alias=True).items() if v is not None
    }

    if len(update) > 0:
        # update the profile with given email with only the fields passed into update (dict)
        update_result = await users_collection.find_one_and_update(
           {"email": email},
           {"$set": update},
           return_document=ReturnDocument.AFTER # makes mongo return updated version of document
        )

        # if user was found and updated, return string version of id
        if update_result is not None:
            update_result["_id"] = str(update_result["_id"])
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"User not found")
    
    raise HTTPException(status_code=400, detail="No fields to update")