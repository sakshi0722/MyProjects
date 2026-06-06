import anthropic
import base64
import json
import re


# ─── Expanded First Aid Database ─────────────────────────────────────────────
# Covers 12 specific injury types so fallback is never generic

FIRST_AID_DB = {
    "snake_bite": {
        "injury_type": "Snake Bite",
        "severity": "severe",
        "first_aid_steps": [
            {"step_number": 1, "instruction": "Keep the victim CALM and still. Movement speeds up venom spread through the body.", "is_critical": True},
            {"step_number": 2, "instruction": "Call 108 (ambulance) IMMEDIATELY. Snake bites are a medical emergency.", "is_critical": True},
            {"step_number": 3, "instruction": "Lay the person down with the bite site BELOW heart level to slow venom spread.", "is_critical": True},
            {"step_number": 4, "instruction": "Remove tight clothing, watches, and jewelry near the bite site — swelling will occur.", "is_critical": True},
            {"step_number": 5, "instruction": "Clean the bite gently with soap and water if available. Cover loosely with a clean cloth.", "is_critical": False},
            {"step_number": 6, "instruction": "Try to remember the snake's appearance (color, size, pattern) — do NOT try to catch it.", "is_critical": False},
            {"step_number": 7, "instruction": "Monitor breathing and consciousness until emergency help arrives.", "is_critical": True},
        ],
        "do_list": [
            "Call 108 immediately",
            "Keep victim still and calm",
            "Keep bite site below heart level",
            "Remove jewelry and tight items near bite",
            "Note the snake's appearance for doctors"
        ],
        "dont_list": [
            "DO NOT cut the bite or try to suck out venom",
            "DO NOT apply ice or a tourniquet",
            "DO NOT give food, water, or alcohol",
            "DO NOT try to catch or kill the snake",
            "DO NOT apply electric shock or heat"
        ],
        "seek_doctor": True,
        "seek_doctor_reason": "ALL snake bites require immediate emergency medical treatment. Anti-venom must be administered by doctors.",
        "estimated_healing": "Several days to weeks depending on snake type and treatment speed",
        "warning_signs": [
            "Swelling spreading rapidly from bite site",
            "Difficulty breathing or swallowing",
            "Blurred vision or drooping eyelids",
            "Nausea, vomiting, or dizziness",
            "Numbness or tingling spreading from bite"
        ],
    },

    "scratch": {
        "injury_type": "Scratch / Superficial Abrasion",
        "severity": "mild",
        "first_aid_steps": [
            {"step_number": 1, "instruction": "Wash your hands thoroughly with soap before touching the scratch.", "is_critical": True},
            {"step_number": 2, "instruction": "Rinse the scratch under clean running water for 2–3 minutes to remove dirt.", "is_critical": True},
            {"step_number": 3, "instruction": "Gently clean around the area with mild soap. Avoid getting soap directly in the scratch.", "is_critical": False},
            {"step_number": 4, "instruction": "Pat dry with a clean cloth or sterile gauze. Do not rub.", "is_critical": False},
            {"step_number": 5, "instruction": "Apply a thin layer of antiseptic ointment (Betadine or Dettol cream).", "is_critical": False},
            {"step_number": 6, "instruction": "Cover with a small adhesive bandage if needed. Leave open to air for minor scratches.", "is_critical": False},
        ],
        "do_list": [
            "Keep the scratch clean and dry",
            "Apply antiseptic to prevent infection",
            "Change bandage daily if covered",
            "Check daily for signs of infection"
        ],
        "dont_list": [
            "Don't scratch or pick at the area",
            "Don't use cotton wool directly on the wound",
            "Don't ignore redness spreading beyond the scratch",
            "Don't apply toothpaste or home remedies"
        ],
        "seek_doctor": False,
        "seek_doctor_reason": "See a doctor if scratch is from an animal (risk of rabies), very deep, or shows signs of infection",
        "estimated_healing": "2–5 days for surface scratches",
        "warning_signs": [
            "Redness spreading beyond the scratch area",
            "Yellow or green discharge",
            "Fever or warmth around the area",
            "Scratch from animal — risk of rabies infection"
        ],
    },

    "animal_scratch": {
        "injury_type": "Animal Scratch (Cat / Dog)",
        "severity": "moderate",
        "first_aid_steps": [
            {"step_number": 1, "instruction": "Wash the scratch IMMEDIATELY with soap and running water for at least 5 minutes.", "is_critical": True},
            {"step_number": 2, "instruction": "Apply antiseptic (Betadine/Dettol) generously to the entire scratch area.", "is_critical": True},
            {"step_number": 3, "instruction": "Cover with a clean bandage after antiseptic dries.", "is_critical": False},
            {"step_number": 4, "instruction": "Check the animal's vaccination status — especially for rabies.", "is_critical": True},
            {"step_number": 5, "instruction": "Visit a doctor within 24 hours to assess rabies risk and get anti-rabies vaccination if needed.", "is_critical": True},
            {"step_number": 6, "instruction": "Report stray animal scratches to local animal control.", "is_critical": False},
        ],
        "do_list": [
            "Wash with soap and water for 5+ minutes immediately",
            "Apply antiseptic thoroughly",
            "See a doctor within 24 hours",
            "Get anti-rabies shots if animal is unvaccinated or stray"
        ],
        "dont_list": [
            "Don't delay washing the wound",
            "Don't ignore even minor animal scratches",
            "Don't skip the doctor visit — rabies is fatal if untreated",
            "Don't try to catch or handle the animal"
        ],
        "seek_doctor": True,
        "seek_doctor_reason": "Animal scratches carry risk of rabies and bacterial infection. Anti-rabies vaccination course must be started within 24 hours if animal is stray or unvaccinated.",
        "estimated_healing": "3–7 days for the scratch; rabies vaccination course is 5 doses over 28 days",
        "warning_signs": [
            "Scratch from stray or unknown animal",
            "Redness and swelling increasing after 24 hours",
            "Fever developing after the scratch",
            "Numbness or tingling near the scratch"
        ],
    },

    "cut": {
        "injury_type": "Cut / Laceration",
        "severity": "mild",
        "first_aid_steps": [
            {"step_number": 1, "instruction": "Wash your hands thoroughly before treating the wound.", "is_critical": True},
            {"step_number": 2, "instruction": "Apply gentle pressure with a clean cloth or sterile gauze to stop bleeding.", "is_critical": True},
            {"step_number": 3, "instruction": "Once bleeding stops, rinse the wound under clean running water for 5 minutes.", "is_critical": False},
            {"step_number": 4, "instruction": "Clean around the wound with mild soap. Do not get soap inside the wound.", "is_critical": False},
            {"step_number": 5, "instruction": "Apply an antiseptic cream (e.g., Betadine or Neosporin).", "is_critical": False},
            {"step_number": 6, "instruction": "Cover with a sterile bandage or adhesive dressing.", "is_critical": False},
            {"step_number": 7, "instruction": "Change the dressing daily or when wet/dirty.", "is_critical": False},
        ],
        "do_list": ["Keep the wound clean and dry", "Change dressing daily", "Watch for signs of infection", "Keep tetanus vaccination up to date"],
        "dont_list": ["Don't remove large embedded objects", "Don't use cotton wool directly on wound", "Don't blow on the wound", "Don't ignore signs of infection"],
        "seek_doctor": False,
        "seek_doctor_reason": "Seek doctor if wound is deep, won't stop bleeding, or shows infection signs",
        "estimated_healing": "3–7 days for minor cuts",
        "warning_signs": ["Increased redness or swelling", "Pus or discharge", "Fever above 38°C", "Red streaks spreading from wound"],
    },

    "burn": {
        "injury_type": "Burn",
        "severity": "moderate",
        "first_aid_steps": [
            {"step_number": 1, "instruction": "Remove from heat source immediately. Ensure your own safety first.", "is_critical": True},
            {"step_number": 2, "instruction": "Cool the burn under cool (NOT cold/iced) running water for at least 20 minutes.", "is_critical": True},
            {"step_number": 3, "instruction": "Remove clothing and jewelry near the burn area UNLESS stuck to skin.", "is_critical": True},
            {"step_number": 4, "instruction": "Cover loosely with a clean, non-fluffy material (cling wrap or clean plastic bag).", "is_critical": False},
            {"step_number": 5, "instruction": "Take paracetamol or ibuprofen for pain relief if needed.", "is_critical": False},
        ],
        "do_list": ["Cool with running water for 20 min", "Keep burn covered loosely", "Stay hydrated", "Seek medical help for large burns"],
        "dont_list": ["Don't use ice or iced water", "Don't burst blisters", "Don't apply butter, toothpaste, or oil", "Don't use fluffy cotton dressings"],
        "seek_doctor": True,
        "seek_doctor_reason": "Burns larger than your hand, on face/hands/feet, or deep burns need immediate medical attention",
        "estimated_healing": "1–2 weeks for minor burns",
        "warning_signs": ["Burn larger than 3 inches", "Deep or white/charred skin", "Burn on face or hands", "Signs of infection after 48 hours"],
    },

    "bruise": {
        "injury_type": "Bruise / Contusion",
        "severity": "mild",
        "first_aid_steps": [
            {"step_number": 1, "instruction": "Apply an ice pack wrapped in a cloth to the area for 20 minutes.", "is_critical": False},
            {"step_number": 2, "instruction": "Keep the injured area elevated above heart level if possible.", "is_critical": False},
            {"step_number": 3, "instruction": "Rest and avoid putting weight on the bruised area.", "is_critical": False},
            {"step_number": 4, "instruction": "After 48 hours, apply a warm compress to improve circulation.", "is_critical": False},
            {"step_number": 5, "instruction": "Take over-the-counter pain relief if needed (ibuprofen or paracetamol).", "is_critical": False},
        ],
        "do_list": ["Apply ice in first 24–48 hours", "Rest the injured area", "Elevate if possible", "Use warm compress after 48 hours"],
        "dont_list": ["Don't apply ice directly to skin", "Don't massage a fresh bruise", "Don't ignore severe pain or swelling"],
        "seek_doctor": False,
        "seek_doctor_reason": "Seek doctor if very painful, swollen, or near the eye/head",
        "estimated_healing": "1–2 weeks depending on severity",
        "warning_signs": ["Extreme swelling", "Cannot move the area", "Bruise near the eye or head", "Bruise without any injury"],
    },

    "sprain": {
        "injury_type": "Sprain",
        "severity": "moderate",
        "first_aid_steps": [
            {"step_number": 1, "instruction": "REST — Stop the activity and rest the injured joint.", "is_critical": True},
            {"step_number": 2, "instruction": "ICE — Apply ice pack wrapped in cloth for 15–20 minutes every 2–3 hours.", "is_critical": True},
            {"step_number": 3, "instruction": "COMPRESSION — Wrap with a bandage to reduce swelling. Not too tight.", "is_critical": False},
            {"step_number": 4, "instruction": "ELEVATION — Raise the injured limb above heart level.", "is_critical": False},
            {"step_number": 5, "instruction": "Take ibuprofen to reduce pain and swelling.", "is_critical": False},
        ],
        "do_list": ["Follow RICE method", "Keep off the joint for 24–48 hours", "Use crutches if needed"],
        "dont_list": ["Don't put weight on severe sprains", "Don't apply heat in first 48 hours", "Don't ignore if you heard a pop"],
        "seek_doctor": True,
        "seek_doctor_reason": "If you heard a pop, cannot bear weight, or no improvement after 2–3 days",
        "estimated_healing": "1–4 weeks depending on severity",
        "warning_signs": ["Severe swelling or bruising", "Cannot move the joint", "Numbness or tingling", "Heard a popping sound"],
    },

    "insect_sting": {
        "injury_type": "Insect Sting / Bee Sting",
        "severity": "mild",
        "first_aid_steps": [
            {"step_number": 1, "instruction": "Remove the stinger by scraping it out sideways with a credit card or fingernail. Do NOT squeeze it.", "is_critical": True},
            {"step_number": 2, "instruction": "Wash the area with soap and water.", "is_critical": False},
            {"step_number": 3, "instruction": "Apply a cold pack or ice wrapped in cloth for 10 minutes to reduce swelling.", "is_critical": False},
            {"step_number": 4, "instruction": "Apply calamine lotion or hydrocortisone cream to reduce itching.", "is_critical": False},
            {"step_number": 5, "instruction": "Take an antihistamine (e.g., cetirizine) to reduce allergic reaction.", "is_critical": False},
            {"step_number": 6, "instruction": "Monitor for signs of severe allergic reaction (anaphylaxis) for 30 minutes.", "is_critical": True},
        ],
        "do_list": ["Scrape out stinger immediately", "Apply cold compress", "Take antihistamine", "Monitor for allergic reaction"],
        "dont_list": ["Don't squeeze the stinger", "Don't scratch the area", "Don't ignore spreading redness or difficulty breathing"],
        "seek_doctor": False,
        "seek_doctor_reason": "Call 108 immediately if breathing difficulty, throat swelling, or widespread rash develops — this is anaphylaxis",
        "estimated_healing": "1–3 days for local swelling",
        "warning_signs": ["Difficulty breathing or swallowing", "Swelling of face, lips, or throat", "Rapid heartbeat or dizziness", "Hives spreading beyond sting site"],
    },

    "nosebleed": {
        "injury_type": "Nosebleed (Epistaxis)",
        "severity": "mild",
        "first_aid_steps": [
            {"step_number": 1, "instruction": "Sit upright and lean FORWARD slightly — not backward. Leaning back causes blood to go to throat.", "is_critical": True},
            {"step_number": 2, "instruction": "Pinch the soft part of the nose (just below the bridge) firmly for 10–15 minutes without releasing.", "is_critical": True},
            {"step_number": 3, "instruction": "Breathe through your mouth while pinching.", "is_critical": False},
            {"step_number": 4, "instruction": "Apply a cold wet cloth to the bridge of the nose.", "is_critical": False},
            {"step_number": 5, "instruction": "After bleeding stops, avoid blowing your nose for several hours.", "is_critical": False},
        ],
        "do_list": ["Lean forward, not backward", "Pinch nose for 10–15 minutes continuously", "Breathe through mouth", "Stay calm"],
        "dont_list": ["Don't tilt head back", "Don't stuff tissue deep into nostril", "Don't blow nose immediately after", "Don't resume activity too soon"],
        "seek_doctor": False,
        "seek_doctor_reason": "Seek help if bleeding doesn't stop after 20 minutes, or after a head injury",
        "estimated_healing": "Stops within 10–20 minutes with proper treatment",
        "warning_signs": ["Bleeding not stopping after 20 minutes", "Blood coming from both nostrils", "Nosebleed after a head injury", "Swallowing large amounts of blood"],
    },

    "eye_injury": {
        "injury_type": "Eye Injury / Foreign Object in Eye",
        "severity": "moderate",
        "first_aid_steps": [
            {"step_number": 1, "instruction": "DO NOT rub the eye — this can scratch the cornea or push object deeper.", "is_critical": True},
            {"step_number": 2, "instruction": "Blink rapidly to try to flush out the object with natural tears.", "is_critical": False},
            {"step_number": 3, "instruction": "Rinse the eye with clean water or saline for 15 minutes. Pour gently from inner corner outward.", "is_critical": True},
            {"step_number": 4, "instruction": "If chemical splash: flush continuously with water for 20 minutes immediately.", "is_critical": True},
            {"step_number": 5, "instruction": "Cover eye lightly with clean cloth if object is embedded — do not try to remove it.", "is_critical": False},
            {"step_number": 6, "instruction": "Seek medical attention if pain, blurred vision, or redness persists after rinsing.", "is_critical": True},
        ],
        "do_list": ["Rinse with clean water", "Seek doctor if symptoms persist", "Keep eye gently closed after rinsing"],
        "dont_list": ["Don't rub the eye", "Don't try to remove embedded objects", "Don't ignore pain or blurred vision"],
        "seek_doctor": True,
        "seek_doctor_reason": "Any persistent pain, blurred vision, or embedded object needs immediate eye doctor attention",
        "estimated_healing": "Hours to days depending on severity",
        "warning_signs": ["Blurred or loss of vision", "Severe pain in the eye", "Blood visible in the white of the eye", "Chemical exposure to eye"],
    },

    "fracture": {
        "injury_type": "Suspected Fracture / Broken Bone",
        "severity": "severe",
        "first_aid_steps": [
            {"step_number": 1, "instruction": "DO NOT try to straighten or move the injured limb.", "is_critical": True},
            {"step_number": 2, "instruction": "Immobilize the area — use a splint (rolled newspaper/magazine) to support in current position.", "is_critical": True},
            {"step_number": 3, "instruction": "Apply ice pack wrapped in cloth to reduce swelling. Do not apply directly to skin.", "is_critical": False},
            {"step_number": 4, "instruction": "If bone is visible (open fracture), cover gently with a clean cloth. Do not push it back in.", "is_critical": True},
            {"step_number": 5, "instruction": "Call 108 or transport to nearest emergency room immediately.", "is_critical": True},
            {"step_number": 6, "instruction": "Keep the person warm and calm. Treat for shock if needed.", "is_critical": False},
        ],
        "do_list": ["Immobilize the limb in current position", "Apply ice to reduce swelling", "Call 108 immediately", "Keep person still and calm"],
        "dont_list": ["Don't try to straighten the bone", "Don't move a suspected spinal fracture", "Don't give food or water", "Don't apply heat"],
        "seek_doctor": True,
        "seek_doctor_reason": "All suspected fractures require immediate X-ray and medical treatment. Do not delay.",
        "estimated_healing": "6–8 weeks for most fractures, longer for complex ones",
        "warning_signs": ["Visible bone deformity", "Bone piercing through skin", "Severe swelling or bruising", "Inability to move the limb", "Numbness below the injury"],
    },

    "wound": {
        "injury_type": "Open Wound",
        "severity": "moderate",
        "first_aid_steps": [
            {"step_number": 1, "instruction": "Wash your hands before touching the wound.", "is_critical": True},
            {"step_number": 2, "instruction": "Apply firm pressure with a clean cloth to control bleeding.", "is_critical": True},
            {"step_number": 3, "instruction": "Do not remove embedded objects — stabilize them in place.", "is_critical": True},
            {"step_number": 4, "instruction": "Rinse wound gently with clean water once bleeding is controlled.", "is_critical": False},
            {"step_number": 5, "instruction": "Apply antiseptic and cover with clean bandage.", "is_critical": False},
            {"step_number": 6, "instruction": "Seek medical attention if wound is deep or won't close.", "is_critical": True},
        ],
        "do_list": ["Control bleeding with pressure", "Keep wound clean", "Cover with clean dressing", "Get tetanus shot if needed"],
        "dont_list": ["Don't remove deeply embedded objects", "Don't probe the wound", "Don't use tourniquet unless life-threatening bleeding"],
        "seek_doctor": True,
        "seek_doctor_reason": "All significant open wounds need medical evaluation",
        "estimated_healing": "Varies — 1 to 6 weeks depending on depth",
        "warning_signs": ["Bleeding won't stop after 10 minutes", "Deep or gaping wound", "Wound on face or over a joint", "Numbness around wound"],
    },
}


# ─── Claude Vision Analysis ───────────────────────────────────────────────────

async def analyze_injury_with_ai(image_base64: str, mime_type: str, description: str = "") -> dict:
    """
    Use Claude Vision API to analyze the injury image.
    Falls back to keyword matching if API fails.
    """
    try:
        client = anthropic.Anthropic()

        prompt = f"""You are an emergency first aid expert. Analyze this injury image very carefully.
{f'User description: "{description}"' if description else ''}

IMPORTANT: Give SPECIFIC advice for THIS exact injury. Do NOT give generic wound advice.
For example:
- Snake bite → specific anti-venom and immobilization steps
- Animal scratch → rabies risk and washing protocol  
- Burn → cooling with water steps
- Fracture → immobilization steps
- Insect sting → stinger removal steps

Respond ONLY with a valid JSON object. No markdown, no backticks, no extra text.

{{
  "injury_type": "specific descriptive name (e.g. 'Cat Scratch', 'Snake Bite', 'Second Degree Burn')",
  "severity": "mild",
  "confidence": 0.85,
  "first_aid_steps": [
    {{"step_number": 1, "instruction": "specific step for THIS injury", "is_critical": true}},
    {{"step_number": 2, "instruction": "specific step for THIS injury", "is_critical": false}}
  ],
  "do_list": ["specific do 1", "specific do 2", "specific do 3"],
  "dont_list": ["specific dont 1", "specific dont 2", "specific dont 3"],
  "seek_doctor": false,
  "seek_doctor_reason": "specific reason for THIS injury",
  "estimated_healing": "X days/weeks",
  "warning_signs": ["specific warning 1", "specific warning 2", "specific warning 3"]
}}

Rules:
- severity: exactly mild, moderate, or severe
- first_aid_steps: 5–8 steps specific to this injury
- do_list and dont_list: 3–5 items each
- warning_signs: 3–5 items
- confidence: 0.5 to 1.0
- seek_doctor: true or false
"""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": image_base64,
                            },
                        },
                        {"type": "text", "text": prompt}
                    ],
                }
            ],
        )

        raw = response.content[0].text.strip()
        raw = re.sub(r"```json\s*", "", raw)
        raw = re.sub(r"```\s*", "", raw)
        raw = raw.strip()

        result = json.loads(raw)
        result["source"] = "ai"
        return result

    except Exception as e:
        print(f"⚠️ AI analysis failed: {e}. Using keyword fallback.")
        return get_fallback_first_aid(description)


# ─── Keyword Fallback ─────────────────────────────────────────────────────────

def get_fallback_first_aid(description: str = "") -> dict:
    """
    Keyword-based fallback with 12 specific injury types.
    Snake bite and animal scratch are now separate from generic cuts.
    """
    desc_lower = description.lower()

    # Most specific matches first
    if any(w in desc_lower for w in ["snake", "serpent", "viper", "cobra"]):
        result = FIRST_AID_DB["snake_bite"].copy()

    elif any(w in desc_lower for w in ["dog scratch", "cat scratch", "animal scratch", "pet scratch", "monkey"]):
        result = FIRST_AID_DB["animal_scratch"].copy()

    elif any(w in desc_lower for w in ["fracture", "broken bone", "broken arm", "broken leg", "bone"]):
        result = FIRST_AID_DB["fracture"].copy()

    elif any(w in desc_lower for w in ["eye", "vision", "cornea", "eyelid"]):
        result = FIRST_AID_DB["eye_injury"].copy()

    elif any(w in desc_lower for w in ["nose bleed", "nosebleed", "bleeding nose"]):
        result = FIRST_AID_DB["nosebleed"].copy()

    elif any(w in desc_lower for w in ["bee", "wasp", "sting", "insect bite", "mosquito bite"]):
        result = FIRST_AID_DB["insect_sting"].copy()

    elif any(w in desc_lower for w in ["burn", "hot", "fire", "scald", "boiling"]):
        result = FIRST_AID_DB["burn"].copy()

    elif any(w in desc_lower for w in ["sprain", "twist", "ankle", "wrist sprain"]):
        result = FIRST_AID_DB["sprain"].copy()

    elif any(w in desc_lower for w in ["bruise", "hit", "bump", "contusion", "purple"]):
        result = FIRST_AID_DB["bruise"].copy()

    elif any(w in desc_lower for w in ["cut", "slice", "laceration", "bleeding", "knife"]):
        result = FIRST_AID_DB["cut"].copy()

    elif any(w in desc_lower for w in ["scratch", "scraped", "abrasion", "graze", "pet", "cat", "dog"]):
        result = FIRST_AID_DB["scratch"].copy()

    else:
        result = FIRST_AID_DB["wound"].copy()

    result["confidence"] = 0.70
    result["source"] = "fallback"
    return result