from fastapi import APIRouter
from datetime import datetime
from async_database import async_db

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

HEALTH_TIPS = [
    "💧 Drink at least 8 glasses of water daily to stay hydrated.",
    "🚶 A 30-minute walk every day reduces risk of heart disease by 30%.",
    "🌙 Sleep 7-8 hours daily — it boosts immunity and mental health.",
    "🥗 Eat a rainbow of vegetables — different colors mean different nutrients.",
    "🧘 10 minutes of deep breathing daily reduces stress and BP.",
    "🌞 Get 15 minutes of morning sunlight for natural Vitamin D.",
    "🍋 Start your day with warm lemon water to boost digestion.",
    "🧄 Add haldi, adrak, and lahsun to your food — natural immunity boosters.",
    "📵 Avoid screens 1 hour before sleep for better sleep quality.",
    "🤸 Stretch for 5 minutes every hour if you sit at a desk.",
    "🥛 Have a glass of haldi doodh at night to reduce inflammation.",
    "🍌 Eat a banana daily — it helps with energy, mood, and digestion.",
]


@router.get("/stats/{user_id}")
async def get_dashboard(user_id: str):
    # Get counts
    recovery_count = await async_db["recovery_plans"].count_documents({"user_id": user_id})
    injury_count = await async_db["injury_logs"].count_documents({"user_id": user_id})
    chat_count = await async_db["chat_logs"].count_documents({"user_id": user_id})
    emergency_count = await async_db["emergency_logs"].count_documents({"user_id": user_id})

    # Get recent recovery plan
    recent_recovery = await async_db["recovery_plans"].find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )

    # Get recent injury
    recent_injury = await async_db["injury_logs"].find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )

    # Get user info
    user = await async_db["users"].find_one({"user_id": user_id})

    # Daily tip based on day of year
    tip_index = datetime.utcnow().timetuple().tm_yday % len(HEALTH_TIPS)
    daily_tip = HEALTH_TIPS[tip_index]

    return {
        "stats": {
            "recovery_plans": recovery_count,
            "injuries_analyzed": injury_count,
            "chats": chat_count,
            "emergency_searches": emergency_count
        },
        "recent_recovery": {
            "condition": recent_recovery["plan"]["condition"] if recent_recovery and "plan" in recent_recovery else None,
            "date": recent_recovery["created_at"].strftime("%d %b %Y") if recent_recovery else None
        } if recent_recovery else None,
        "recent_injury": {
            "injury_type": recent_injury.get("injury_type") if recent_injury else None,
            "date": recent_injury["created_at"].strftime("%d %b %Y") if recent_injury else None
        } if recent_injury else None,
        "user": {
            "name": user["name"] if user else "User",
            "email": user["email"] if user else ""
        },
        "daily_tip": daily_tip
    }