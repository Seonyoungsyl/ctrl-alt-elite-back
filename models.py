from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import uuid4

# Authentication Models
class UserSignup(BaseModel):
    accountType: str
    fullName: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# Profile Models
class Profile(BaseModel):
    fullName: str
    email: str
    accountType: str
    mentor_name: Optional[str] = None
    fun_facts: str
    points: int

class UpdateProfile(BaseModel):
    fullName: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    mentor_name: Optional[str] = None
    fun_facts: Optional[str] = None

class ProfileOut(Profile):
    id: str = Field(alias="_id")

# Bucket List Models
class Task(BaseModel):
    id: str = None
    description: str
    completed: bool = False

    def model_post_init(self, __context):
        if self.id is None:
            self.id = str(uuid4())

class BucketList(BaseModel):
    mentor_name: str
    tasks: List[Task]