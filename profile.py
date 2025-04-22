from fastapi import APIRouter, HTTPException, Body
from database import db
from models import Profile, ProfileOut, UpdateProfile
from pymongo import ReturnDocument

profile_router = APIRouter()
users_collection = db["profiles"]


# GET PROFILE INFO OF USER
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