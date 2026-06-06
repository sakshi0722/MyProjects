from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import base64
from datetime import datetime

from post_recovery.recovery_service import generate_recovery_plan, extract_report_text, get_fallback_plan
from async_database import async_db

router = APIRouter(prefix="/api/recovery", tags=["Recovery"])


@router.post("/generate-plan")
async def generate_plan(
    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    weight_kg: float = Form(...),
    height_cm: float = Form(...),
    food_preference: str = Form(...),
    activity_level: str = Form(...),
    recovery_goal: str = Form(default=""),
    injury_type: str = Form(default=""),
    injury_date: str = Form(default=""),
    allergies: str = Form(default=""),
    health_conditions: str = Form(default=""),
    current_medications: str = Form(default=""),
    report: Optional[UploadFile] = File(default=None)
):
    allergies_list = [a.strip() for a in allergies.split(",") if a.strip()]
    conditions_list = [c.strip() for c in health_conditions.split(",") if c.strip()]
    medications_list = [m.strip() for m in current_medications.split(",") if m.strip()]

    # Combine injury_type into recovery_goal if not set
    if not recovery_goal and injury_type:
        recovery_goal = f"Recovering from {injury_type}"

    patient_info = {
        "user_id": user_id,
        "name": name,
        "age": age,
        "gender": gender,
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "food_preference": food_preference,
        "activity_level": activity_level,
        "recovery_goal": recovery_goal,
        "injury_type": injury_type,
        "injury_date": injury_date,
        "allergies": allergies_list,
        "health_conditions": conditions_list,
        "current_medications": medications_list,
    }

    # Extract text from report image if uploaded
    report_text = ""
    if report and report.filename:
        allowed = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        if report.content_type in allowed:
            contents = await report.read()
            if len(contents) <= 10 * 1024 * 1024:
                image_b64 = base64.b64encode(contents).decode("utf-8")
                report_text = await extract_report_text(image_b64, report.content_type)

    # Generate AI plan
    plan = await generate_recovery_plan(patient_info, report_text)

    # Save to MongoDB
    record = {
        "user_id": user_id,
        "patient_info": patient_info,
        "report_text": report_text,
        "plan": plan,
        "created_at": datetime.utcnow()
    }
    result = await async_db["recovery_plans"].insert_one(record)

    return {
        "plan_id": str(result.inserted_id),
        "patient_info": patient_info,
        "report_summary": report_text,
        **plan
    }


@router.get("/plans/{user_id}")
async def get_user_plans(user_id: str):
    plans = await async_db["recovery_plans"].find(
        {"user_id": user_id}
    ).sort("created_at", -1).to_list(length=10)
    for p in plans:
        p["_id"] = str(p["_id"])
    return plans