from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import re

from async_database import async_db

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    user_id: str
    message: str
    history: Optional[List[Message]] = []


# ─── Knowledge Base ───────────────────────────────────────────────────────────

RESPONSES = {
    # Emergency
    "emergency|ambulance|108|accident|unconscious|not breathing|heart attack|stroke|seizure|faint": {
        "reply": "🚨 **This sounds like an emergency!**\n\nCall **108** (Ambulance) immediately.\n\nWhile waiting:\n→ Keep the person calm and still\n→ Do not give food or water\n→ Use our **Emergency module** to find the nearest hospital\n\n📞 **Call 108 NOW**",
        "module": "emergency"
    },

    # Fever
    "fever|temperature|bukhar|103|104|high temp": {
        "reply": "🌡️ **For fever:**\n\n→ Take Paracetamol (Crocin/Dolo 650) every 6 hours\n→ Drink plenty of fluids — ORS, coconut water, dal ka pani\n→ Apply a cool wet cloth on forehead\n→ Wear light cotton clothes\n→ Rest completely\n\n⚠️ See a doctor if fever is above 103°F or lasts more than 3 days."
    },

    # Cold and cough
    "cold|cough|runny nose|sore throat|congestion|khansi|nazla": {
        "reply": "🤧 **For cold & cough:**\n\n→ Drink warm water with tulsi, ginger and honey\n→ Steam inhalation 2-3 times a day\n→ Gargle with warm salt water\n→ Take rest and avoid cold foods\n→ Haldi doodh (turmeric milk) at night helps\n\n⚠️ See a doctor if cough lasts more than 2 weeks or you have chest pain."
    },

    # Headache
    "headache|sir dard|migraine|head pain": {
        "reply": "🤕 **For headache:**\n\n→ Drink a full glass of water first (dehydration is common cause)\n→ Rest in a quiet, dark room\n→ Apply cold or warm compress on forehead\n→ Light massage on temples with coconut oil\n→ Take Paracetamol if needed\n\n⚠️ See a doctor immediately if headache is sudden and severe, or with stiff neck/vomiting."
    },

    # Cut and bleeding
    "cut|bleeding|wound|blood|lacerati": {
        "reply": "🩸 **For cuts and bleeding:**\n\n→ Press firmly with clean cloth for 5-10 minutes\n→ Rinse with clean water\n→ Apply antiseptic (Dettol/Savlon)\n→ Cover with bandage\n→ Do NOT remove cloth if blood soaks through — add more on top\n\n⚠️ Go to hospital if bleeding doesn't stop in 10 mins, wound is deep, or you need stitches.\n\n📸 Use our **Minor Injury module** to get AI first aid guidance!"
    },

    # Burn
    "burn|jalana|scald|hot water|fire": {
        "reply": "🔥 **For burns:**\n\n→ Cool under running cold water for 10-20 minutes\n→ Do NOT use ice, butter, or toothpaste\n→ Cover loosely with clean cloth\n→ Take Paracetamol for pain\n\n⚠️ Go to hospital immediately if:\n- Burn is larger than your palm\n- Burn is on face, hands, or private parts\n- Skin looks white or black\n\n📸 Use our **Minor Injury module** for AI guidance!"
    },

    # Sprain
    "sprain|twist|ankle|moch|swelling|swell": {
        "reply": "🦵 **For sprains:**\n\nFollow **RICE method:**\n→ **R**est — stop using the injured part\n→ **I**ce — apply ice pack for 20 mins every hour\n→ **C**ompression — wrap with bandage\n→ **E**levation — keep it raised above heart level\n\nTake Ibuprofen for pain and swelling.\n\n⚠️ Get an X-ray if you cannot put any weight on it."
    },

    # Stomach pain
    "stomach|pet dard|abdomen|nausea|vomit|diarrhea|loose motion|acidity|gas|bloat": {
        "reply": "🫃 **For stomach problems:**\n\n→ Drink ORS or nimbu pani with salt and sugar\n→ Eat light food — khichdi, curd rice, banana\n→ Avoid spicy, oily food\n→ Take Pantoprazole for acidity\n→ Rest and stay hydrated\n\n⚠️ See a doctor if pain is severe, there is blood in stool, or vomiting doesn't stop after 24 hours."
    },

    # Diabetes
    "diabetes|sugar|blood sugar|insulin|diabetic": {
        "reply": "🩺 **Diabetes management tips:**\n\n→ Eat small meals every 3-4 hours\n→ Avoid white rice, maida, sweets, fruit juices\n→ Prefer: brown rice, jowar roti, methi, karela, dalia\n→ Walk 30 minutes daily\n→ Check blood sugar regularly\n→ Never skip medications\n\n🏥 Use our **Recovery module** for a personalised diabetic diet plan!"
    },

    # Blood pressure
    "blood pressure|bp|hypertension|high bp|low bp": {
        "reply": "💊 **Blood pressure tips:**\n\n**High BP:**\n→ Reduce salt intake\n→ Avoid fried and processed food\n→ Exercise regularly\n→ Manage stress with meditation\n\n**Low BP:**\n→ Drink ORS or nimbu pani\n→ Eat small frequent meals\n→ Increase salt and water intake slightly\n\n⚠️ Always take BP medications as prescribed. Never stop suddenly."
    },

    # Diet
    "diet|food|khaana|nutrition|eat|meal|weight loss|weight gain": {
        "reply": "🥗 **Healthy Indian diet tips:**\n\n→ Include dal, sabzi, roti, curd in every meal\n→ Eat seasonal fruits and vegetables\n→ Drink 8-10 glasses of water daily\n→ Avoid packaged/junk food\n→ Have haldi doodh at night for immunity\n→ Eat breakfast — poha, upma, idli are great options\n\n🏥 Use our **Recovery module** for a personalised 7-day diet plan!"
    },

    # Exercise
    "exercise|workout|yoga|walk|gym|physical": {
        "reply": "🏃 **Exercise recommendations:**\n\n→ Walk 30-45 minutes daily — best medicine!\n→ Yoga and pranayama for flexibility and breathing\n→ Surya namaskar — full body workout\n→ Avoid heavy exercise if recovering from illness\n→ Start slow and increase gradually\n\n🏥 Use our **Recovery module** for a personalised exercise plan based on your condition!"
    },

    # Sleep
    "sleep|insomnia|neend|tired|fatigue|rest": {
        "reply": "😴 **For better sleep:**\n\n→ Sleep and wake at the same time daily\n→ Avoid phone/screen 1 hour before bed\n→ Drink warm milk with haldi before sleeping\n→ Keep room dark and cool\n→ Light walk after dinner helps\n→ Avoid tea/coffee after 5pm\n\n⚠️ See a doctor if you haven't slept well for more than 2 weeks."
    },

    # Pimple / skin
    "pimple|acne|skin|rash|itch|allergy|khujli": {
        "reply": "✨ **For pimples and skin issues:**\n\n→ Wash face with mild facewash twice daily\n→ Do not pop or squeeze pimples\n→ Apply neem paste or aloe vera gel\n→ Drink plenty of water\n→ Reduce sugar and dairy if acne is frequent\n→ Change pillow covers weekly\n\n⚠️ See a dermatologist if rash is spreading, painful, or with fever."
    },

    # Recovery
    "recover|surgery|operation|post op|rehabilitation|healing": {
        "reply": "🏥 **Recovery tips after surgery/illness:**\n\n→ Follow doctor's instructions strictly\n→ Eat protein-rich foods — dal, paneer, eggs, chicken\n→ Stay hydrated\n→ Rest but do gentle movement as advised\n→ Take all medications on time\n→ Attend all follow-up appointments\n\n✨ Use our **Recovery module** for a complete personalised 7-day Indian diet + exercise plan!"
    },

    # Modules info
    "module|feature|app|what can you do|help|how": {
        "reply": "👋 **MediConnect can help you with:**\n\n🚨 **Emergency** — Find nearest hospitals, voice search, call contacts\n\n🩹 **Minor Injury** — Upload injury photo → Get AI first aid guide\n\n🏥 **Recovery** — Fill your details → Get 7-day Indian diet + exercise plan\n\n💬 **MediBot** (me!) — Ask any health question\n\nWhat would you like help with today?"
    },

    # Greeting
    "hi|hello|hey|namaste|hii|good morning|good evening|good afternoon": {
        "reply": "👋 **Namaste! I'm MediBot.**\n\nI'm your MediConnect health assistant. I can help you with:\n→ First aid guidance\n→ Common illness remedies\n→ Diet and nutrition tips\n→ Recovery advice\n→ Directing you to the right module\n\nWhat health question can I help you with today?"
    },

    # Thank you
    "thank|thanks|shukriya|धन्यवाद|helpful": {
        "reply": "😊 You're welcome! Stay healthy.\n\nRemember — for any emergency, call **108** immediately. Take care! 🌟"
    },
}

DEFAULT_RESPONSE = "🤔 I'm not sure about that specific question. For accurate medical advice, please consult a doctor.\n\nI can help you with:\n→ First aid (cuts, burns, sprains)\n→ Common illnesses (fever, cold, stomach)\n→ Diet and recovery tips\n→ Finding hospitals (Emergency module)\n\nFor emergencies, call **108** immediately. 🚨"


def find_response(message: str) -> str:
    msg = message.lower().strip()
    for pattern, data in RESPONSES.items():
        keywords = pattern.split("|")
        if any(kw in msg for kw in keywords):
            return data["reply"]
    return DEFAULT_RESPONSE


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.post("/message")
async def chat(request: ChatRequest):
    try:
        reply = find_response(request.message)

        await async_db["chat_logs"].insert_one({
            "user_id": request.user_id,
            "user_message": request.message,
            "bot_reply": reply,
            "timestamp": datetime.utcnow()
        })

        return {"reply": reply, "status": "ok"}

    except Exception as e:
        print(f"Chatbot error: {e}")
        return {
            "reply": "Sorry, something went wrong. For emergencies please call **108** immediately. 🚨",
            "status": "error"
        }


@router.get("/history/{user_id}")
async def get_history(user_id: str):
    logs = await async_db["chat_logs"].find(
        {"user_id": user_id}
    ).sort("timestamp", -1).to_list(length=50)
    for l in logs:
        l["_id"] = str(l["_id"])
    return logs