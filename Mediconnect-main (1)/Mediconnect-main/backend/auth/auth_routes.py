from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import hashlib

from async_database import async_db

router = APIRouter(prefix="/api/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_user_id(email: str) -> str:
    return hashlib.md5(email.encode()).hexdigest()[:12]


@router.post("/register")
async def register(req: RegisterRequest):
    existing = await async_db["users"].find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered. Please login.")

    user_id = generate_user_id(req.email)
    user = {
        "user_id": user_id,
        "name": req.name,
        "email": req.email,
        "password": hash_password(req.password),
        "created_at": datetime.utcnow()
    }
    await async_db["users"].insert_one(user)

    return {
        "message": "Registration successful!",
        "user_id": user_id,
        "name": req.name,
        "email": req.email
    }


@router.post("/login")
async def login(req: LoginRequest):
    user = await async_db["users"].find_one({"email": req.email})
    if not user:
        raise HTTPException(status_code=404, detail="No account found with this email.")

    if user["password"] != hash_password(req.password):
        raise HTTPException(status_code=400, detail="Incorrect password.")

    return {
        "message": "Login successful!",
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"]
    }


@router.get("/user/{user_id}")
async def get_user(user_id: str):
    user = await async_db["users"].find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"]
    }
