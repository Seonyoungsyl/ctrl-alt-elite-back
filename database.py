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
db = client["bootcamp"]