from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import base64

from minor_injury.minor_service import analyze_injury_with_ai, get_fallback_first_aid
from async_database import async_db
from datetime import datetime

router = APIRouter(prefix="/api/minor-injury", tags=["Minor Injury"])


@router.post("/analyze")
async def analyze_injury(
    image: UploadFile = File(...),
    user_id: str = Form(default="anonymous"),
    description: str = Form(default="")
):
    """
    Accepts an injury photo upload + optional description.
    Returns detailed first aid guidance.
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a JPEG, PNG, or WebP image."
        )

    # Validate file size (max 5MB)
    contents = await image.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large. Max size is 5MB.")

    # Convert to base64 for Claude Vision API
    image_base64 = base64.b64encode(contents).decode("utf-8")
    mime_type = image.content_type

    # Analyze with AI
    result = await analyze_injury_with_ai(image_base64, mime_type, description)

    # Log to MongoDB
    await async_db["injury_logs"].insert_one({
        "user_id": user_id,
        "description": description,
        "injury_type": result.get("injury_type", "unknown"),
        "severity": result.get("severity", "unknown"),
        "seek_doctor": result.get("seek_doctor", False),
        "source": result.get("source", "ai"),
        "timestamp": datetime.utcnow()
    })

    return result


@router.get("/history/{user_id}")
async def get_history(user_id: str):
    """Get injury analysis history for a user."""
    logs = await async_db["injury_logs"].find(
        {"user_id": user_id}
    ).sort("timestamp", -1).to_list(length=20)

    for log in logs:
        log["_id"] = str(log["_id"])
    return logs


@router.get("/first-aid/{injury_type}")
async def get_first_aid_guide(injury_type: str):
    """Get first aid guide for a specific injury type by keyword."""
    result = get_fallback_first_aid(injury_type)
    return result
