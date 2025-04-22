from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import io
from database import db
from typing import List

router = APIRouter(prefix="/images", tags=["images"])

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
    
    # Saving the file info to MongoDB - Using the motor async client directly
    # First, create a file entry
    file_doc = {
        "filename": file.filename,
        "metadata": metadata,
        "length": len(contents)
    }
    result = await db.fs.files.insert_one(file_doc)
    file_id = result.inserted_id
    
    # Then store the file data
    chunk_doc = {
        "files_id": file_id,
        "n": 0,  # Chunk number
        "data": contents
    }
    await db.fs.chunks.insert_one(chunk_doc)
    
    return {
        "image_id": str(file_id),
        "filename": file.filename,
        "content_type": content_type
    }

@router.get("/{image_id}")
async def get_image(image_id: str):
    """
    Grabbing an image by its ID so we can display it
    """
    try:
        # Looking up the file info using Motor's async methods
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
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing images: {str(e)}")

@router.delete("/{image_id}")
async def delete_image(image_id: str):
    """
    Getting rid of an image we don't need anymore
    """
    try:
        # Converting string ID to ObjectId
        obj_id = ObjectId(image_id)
        
        # Cleaning up both the file info and the actual data
        delete_file_result = await db.fs.files.delete_one({"_id": obj_id})
        delete_chunks_result = await db.fs.chunks.delete_many({"files_id": obj_id})
        
        if delete_file_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Image not found")
            
        return {"message": "Image deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}") 