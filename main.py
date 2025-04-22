from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import auth_router
from profile import profile_router
from group import group_router
from bucket_list import bucketlist_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # frontend port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers for authentication (login/sign up), profile updates/viewing
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(profile_router, prefix="/profile", tags=["profile"])
app.include_router(group_router, prefix="/group", tags=["group"])
app.include_router(bucketlist_router, prefix="/bucketlist", tags=["bucketlist"])