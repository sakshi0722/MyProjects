from fastapi import APIRouter
from datetime import datetime

# ← NO "backend." prefix — you're already inside the backend folder
from emergency.emergency_model import EmergencyRequest, UserContacts
from emergency.emergency_service import classify_emergency, rank_hospitals, seed_hospitals
from async_database import async_db

router = APIRouter(prefix="/api/emergency", tags=["Emergency"])


# ─── Find Nearest Hospitals ───────────────────────────────────────────────────

@router.post("/find-hospitals")
async def find_hospitals(req: EmergencyRequest):
    emergency_type = classify_emergency(req.input_text) if req.input_text else req.emergency_type

    all_hospitals = await async_db["hospitals"].find({}).to_list(length=100)
    ranked = rank_hospitals(all_hospitals, req.latitude, req.longitude, emergency_type)

    await async_db["emergency_logs"].insert_one({
        "user_id": req.user_id,
        "input_text": req.input_text,
        "emergency_type": emergency_type,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "timestamp": datetime.utcnow(),
        "hospitals_found": len(ranked),
    })

    return {
        "emergency_type": emergency_type,
        "user_location": {"lat": req.latitude, "lng": req.longitude},
        "hospitals": ranked,
        "recommended": ranked[0] if ranked else None,
    }


# ─── Get All Hospitals ────────────────────────────────────────────────────────

@router.get("/hospitals")
async def get_all_hospitals():
    hospitals = await async_db["hospitals"].find({}).to_list(length=100)
    for h in hospitals:
        h["_id"] = str(h["_id"])
    return hospitals


# ─── Get Emergency Contacts ───────────────────────────────────────────────────

@router.get("/contacts/{user_id}")
async def get_contacts(user_id: str):
    doc = await async_db["user_contacts"].find_one({"user_id": user_id})

    if not doc:
        return {
            "user_id": user_id,
            "contacts": [
                {"name": "Ambulance (National)", "phone": "108", "relation": "Emergency Services"},
                {"name": "Police",               "phone": "100", "relation": "Emergency Services"},
                {"name": "Fire Brigade",          "phone": "101", "relation": "Emergency Services"},
            ],
        }

    doc["_id"] = str(doc["_id"])
    return doc


# ─── Save Emergency Contacts ──────────────────────────────────────────────────

@router.post("/contacts")
async def save_contacts(data: UserContacts):
    default_contacts = [
        {"name": "Ambulance (National)", "phone": "108", "relation": "Emergency Services"},
        {"name": "Police",               "phone": "100", "relation": "Emergency Services"},
    ]

    personal = [c.dict() for c in data.contacts]
    all_contacts = default_contacts + personal

    existing = await async_db["user_contacts"].find_one({"user_id": data.user_id})

    if existing:
        await async_db["user_contacts"].update_one(
            {"user_id": data.user_id},
            {"$set": {"contacts": all_contacts, "updated_at": datetime.utcnow()}},
        )
    else:
        await async_db["user_contacts"].insert_one({
            "user_id": data.user_id,
            "contacts": all_contacts,
            "created_at": datetime.utcnow(),
        })

    return {"message": "Contacts saved successfully", "total": len(all_contacts)}


# ─── Emergency History ────────────────────────────────────────────────────────

@router.get("/logs/{user_id}")
async def get_logs(user_id: str):
    logs = await async_db["emergency_logs"].find(
        {"user_id": user_id}
    ).sort("timestamp", -1).to_list(length=20)

    for log in logs:
        log["_id"] = str(log["_id"])
    return logs