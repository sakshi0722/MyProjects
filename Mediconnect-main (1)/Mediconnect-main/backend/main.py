from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import db

from emergency.emergency_routes import router as emergency_router
from minor_injury.minor_routes import router as minor_router
from post_recovery.recovery_routes import router as recovery_router
from chatbot.chatbot_routes import router as chatbot_router
from auth.auth_routes import router as auth_router
from auth.dashboard_routes import router as dashboard_router

from emergency.emergency_service import seed_hospitals
from async_database import async_db

app = FastAPI(title="MediConnect API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(emergency_router)
app.include_router(minor_router)
app.include_router(recovery_router)
app.include_router(chatbot_router)

@app.on_event("startup")
async def startup():
    await seed_hospitals(async_db)

@app.get("/")
def home():
    return {"status": "MediConnect backend running"}

@app.get("/test-db")
def test_db():
    return {"collections": db.list_collection_names()}