import math
from datetime import datetime


# ─── Emergency Classification ─────────────────────────────────────────────────

def classify_emergency(text: str) -> str:
    text_lower = text.lower()

    if any(w in text_lower for w in ["heart", "chest", "cardiac", "pulse", "heart attack"]):
        return "cardiac"
    elif any(w in text_lower for w in ["accident", "crash", "injury", "fracture", "broken", "bleeding"]):
        return "trauma"
    elif any(w in text_lower for w in ["breath", "asthma", "suffocating", "oxygen", "can't breathe"]):
        return "respiratory"
    elif any(w in text_lower for w in ["stroke", "paralysis", "unconscious", "faint", "seizure"]):
        return "neurological"
    elif any(w in text_lower for w in ["burn", "fire", "chemical", "acid"]):
        return "burns"
    elif any(w in text_lower for w in ["child", "baby", "infant", "pediatric", "kid"]):
        return "pediatric"

    return "general"


# ─── Distance & ETA ───────────────────────────────────────────────────────────

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def estimate_eta(distance_km: float) -> int:
    speed_kmh = 50
    return max(5, int((distance_km / speed_kmh) * 60))


# ─── Hospital Ranking ─────────────────────────────────────────────────────────

def rank_hospitals(hospitals: list, user_lat: float, user_lng: float, emergency_type: str) -> list:
    results = []

    for h in hospitals:
        dist = haversine(user_lat, user_lng, h["latitude"], h["longitude"])
        eta = estimate_eta(dist)
        is_specialized = emergency_type in h.get("specialties", [])

        results.append({
            "id": str(h["_id"]),
            "name": h["name"],
            "address": h["address"],
            "latitude": h["latitude"],
            "longitude": h["longitude"],
            "phone": h["phone"],
            "specialties": h.get("specialties", []),
            "rating": h.get("rating", 4.0),
            "available_beds": h.get("available_beds", 0),
            "distance_km": round(dist, 2),
            "eta_minutes": eta,
            "is_specialized": is_specialized,
        })

    results.sort(key=lambda x: (not x["is_specialized"], x["distance_km"]))
    return results[:5]


# ─── Seed Data ────────────────────────────────────────────────────────────────

async def seed_hospitals(db) -> None:
    """Insert sample hospitals only if collection is empty."""
    count = await db["hospitals"].count_documents({})
    if count > 0:
        return

    hospitals = [
        {
            "name": "Yashwantrao Chavan Memorial Hospital",
            "address": "Pimpri, Pune - 411018",
            "latitude": 18.6298,
            "longitude": 73.7997,
            "phone": "+91-20-27427400",
            "specialties": ["cardiac", "trauma", "general", "pediatric"],
            "rating": 4.2,
            "available_beds": 45,
        },
        {
            "name": "Aditya Birla Memorial Hospital",
            "address": "Chinchwad, Pune - 411033",
            "latitude": 18.6484,
            "longitude": 73.8067,
            "phone": "+91-20-30715000",
            "specialties": ["cardiac", "neurological", "burns", "general"],
            "rating": 4.5,
            "available_beds": 30,
        },
        {
            "name": "Lokmanya Hospital",
            "address": "Chinchwad Station, Pune - 411033",
            "latitude": 18.6520,
            "longitude": 73.8012,
            "phone": "+91-20-30260260",
            "specialties": ["trauma", "general", "respiratory"],
            "rating": 4.1,
            "available_beds": 20,
        },
        {
            "name": "Jehangir Hospital",
            "address": "Sassoon Road, Pune - 411001",
            "latitude": 18.5236,
            "longitude": 73.8670,
            "phone": "+91-20-66814444",
            "specialties": ["cardiac", "neurological", "burns", "pediatric", "general"],
            "rating": 4.7,
            "available_beds": 60,
        },
        {
            "name": "Ruby Hall Clinic",
            "address": "Wanowrie, Pune - 411040",
            "latitude": 18.5089,
            "longitude": 73.9021,
            "phone": "+91-20-26168888",
            "specialties": ["trauma", "cardiac", "general"],
            "rating": 4.4,
            "available_beds": 40,
        },
    ]

    await db["hospitals"].insert_many(hospitals)
    print("✅ Hospital data seeded successfully.")