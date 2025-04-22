from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from gridfs import GridFS
from bson import ObjectId
import io
from database import db
from typing import List

router = APIRouter(prefix="/images", tags=["images"])

# Setting up GridFS for storing our images
fs = GridFS(db)

# Models to help us keep track of image data
class ImageResponse(dict):
    image_id: str
    filename: str
    content_type: str

@router.post("/upload", status_code=201)
async def upload_image(file: UploadFile = File(...), user_id: str = None):
    """
    Uploading an image file and linking it to a user if needed
    """
    # Making sure we're only accepting image files
    content_type = file.content_type
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Reading the file contents
    contents = await file.read()
    
    # Creating some helpful metadata to keep track of the image
    metadata = {"filename": file.filename, "content_type": content_type}
    if user_id:
        metadata["user_id"] = user_id
    
    # Saving the file info to MongoDB
    image_id = await db.fs.files.insert_one({
        "filename": file.filename,
        "metadata": metadata
    })
    
    # Storing the actual image data in chunks
    await db.fs.chunks.insert_one({
        "files_id": image_id.inserted_id,
        "data": contents
    })
    
    return {
        "image_id": str(image_id.inserted_id),
        "filename": file.filename,
        "content_type": content_type
    }

@router.get("/{image_id}")
async def get_image(image_id: str):
    """
    Grabbing an image by its ID so we can display it
    """
    try:
        # Looking up the file info
        file_data = await db.fs.files.find_one({"_id": ObjectId(image_id)})
        if not file_data:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Getting the actual image data
        chunk = await db.fs.chunks.find_one({"files_id": ObjectId(image_id)})
        if not chunk:
            raise HTTPException(status_code=404, detail="Image data not found")
        
        # Figuring out what type of image it is
        content_type = file_data.get("metadata", {}).get("content_type", "image/jpeg")
        
        # Sending the image back as a stream
        return StreamingResponse(
            io.BytesIO(chunk["data"]),
            media_type=content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving image: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_images(user_id: str):
    """
    Finding all images that belong to a specific user
    """
    # Looking for all images linked to this user
    cursor = db.fs.files.find({"metadata.user_id": user_id})
    
    # Building a list of all the images we find
    images = []
    async for doc in cursor:
        images.append({
            "image_id": str(doc["_id"]),
            "filename": doc["filename"],
            "content_type": doc.get("metadata", {}).get("content_type", "image/jpeg")
        })
    
    return images

@router.delete("/{image_id}")
async def delete_image(image_id: str):
    """
    Getting rid of an image we don't need anymore
    """
    try:
        # Cleaning up both the file info and the actual data
        await db.fs.files.delete_one({"_id": ObjectId(image_id)})
        await db.fs.chunks.delete_many({"files_id": ObjectId(image_id)})
        
        return {"message": "Image deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}") 