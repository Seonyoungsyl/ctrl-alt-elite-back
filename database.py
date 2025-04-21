from fastapi import FastAPI, Body, APIRouter, HTTPException
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List
from bson import ObjectId
import os
from dotenv import load_dotenv
from models import Profile, ProfileOut, UpdateProfile
from pymongo import ReturnDocument

# Load environment variables from .env file
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

# MongoDB connection
client = AsyncIOMotorClient(MONGODB_URI)
db = client["app"]
users_collection = db["profiles"]

app = FastAPI() # do we need to change this to a router like we did for profile.py and auth.py?

# GET LIST OF USERS FOR SAME MENTOR
@app.get("/group/{mentor_name}", response_model=List[ProfileOut])
async def get_members(mentor_name:str):
    cursor = users_collection.find({"mentor_name": mentor_name})
    
    if not cursor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    members = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"]) # convert ObjectId to string for response
        members.append(doc)
    return members

# GET PROFILE INFO ABOUT USER
@app.get("/profile/{email}", response_model=ProfileOut)
async def update_profile(email:str):
    user = await users_collection.find_one({"email":email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["_id"] = str(user["_id"])
    return user

# UPDATE USER INFORMATION
@app.put("/profile/{email}", response_model=Profile)
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

# UPDATE POINT TOTALS FOR GROUP
# change the URL thing after bucketlist backend is complete
@app.put("/group/{mentor_name}/bucketlist/complete")
async def update_points(mentor_name:str, points_added:int):
    members = users_collection.find({"mentor_name": mentor_name})
    updated = 0

    # use async for loop since cursor returned by .find is async
    async for member in members:
        result = await users_collection.update_one(
            {"_id": member["_id"]},
            {"$inc": {"points": points_added}}
        )

        # increment updated var if number of docs modified > 0
        if result.modified_count > 0:
            updated += 1
    
    if updated == 0:
        raise HTTPException(status_code=404, detail="No members updated")
    return {"message": "Updated group points"}

