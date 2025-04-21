from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

# Authentication Models
class UserSignup(BaseModel):
    accountType: str
    fullName: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# Profile Model
class Profile(BaseModel):
    fullName: str
    email: str
    role: str
    mentor_name: str
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

    