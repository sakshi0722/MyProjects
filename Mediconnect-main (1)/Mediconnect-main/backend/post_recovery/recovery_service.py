import anthropic
import base64
import json
import re


# ─── Generate Recovery Plan via Claude AI ────────────────────────────────────

async def generate_recovery_plan(patient_info: dict, report_text: str = "") -> dict:
    """
    Uses Claude AI to generate a personalized Indian diet plan
    and exercise plan based on patient info and doctor's report.
    """
    try:
        client = anthropic.Anthropic()

        food_pref = patient_info.get("food_preference", "veg")
        allergies = ", ".join(patient_info.get("allergies", [])) or "None"
        conditions = ", ".join(patient_info.get("health_conditions", [])) or "None"
        medications = ", ".join(patient_info.get("current_medications", [])) or "None"

        prompt = f"""You are an expert Indian nutritionist and physiotherapist creating a personalized recovery plan.

PATIENT DETAILS:
- Name: {patient_info.get('name')}
- Age: {patient_info.get('age')} years
- Gender: {patient_info.get('gender')}
- Weight: {patient_info.get('weight_kg')} kg
- Height: {patient_info.get('height_cm')} cm
- Food Preference: {food_pref}
- Allergies: {allergies}
- Health Conditions: {conditions}
- Current Medications: {medications}
- Activity Level: {patient_info.get('activity_level')}
- Recovery Goal: {patient_info.get('recovery_goal', 'General recovery')}

DOCTOR'S REPORT SUMMARY:
{report_text if report_text else 'No report uploaded. Generate plan based on patient details and recovery goal.'}

INSTRUCTIONS:
1. Create a 7-day INDIAN diet plan using common Indian foods (dal, roti, rice, sabzi, curd, etc.)
2. Meals must respect food preference ({food_pref}) and avoid listed allergies
3. Create an appropriate exercise plan considering the recovery condition
4. If condition involves surgery/injury, mark exercises to AVOID
5. All food items must be practical Indian household meals
6. Include specific quantities (e.g., "2 rotis", "1 katori dal", "1 cup curd")

Respond ONLY with valid JSON. No markdown, no backticks, no extra text:

{{
  "condition": "detected condition from report or recovery goal",
  "diet_plan": [
    {{
      "day": "Day 1",
      "breakfast": [
        {{"name": "Oats Upma", "quantity": "1 bowl", "calories": 250, "notes": "Add vegetables"}},
        {{"name": "Banana", "quantity": "1 medium", "calories": 90, "notes": null}}
      ],
      "mid_morning": [
        {{"name": "Coconut Water", "quantity": "1 glass", "calories": 45, "notes": "Hydrating"}}
      ],
      "lunch": [
        {{"name": "Brown Rice", "quantity": "1 katori", "calories": 215, "notes": null}},
        {{"name": "Dal Tadka", "quantity": "1 katori", "calories": 150, "notes": "High protein"}},
        {{"name": "Palak Sabzi", "quantity": "1 katori", "calories": 80, "notes": "Iron rich"}},
        {{"name": "Curd", "quantity": "1 small bowl", "calories": 60, "notes": "Probiotic"}}
      ],
      "evening_snack": [
        {{"name": "Roasted Chana", "quantity": "1 handful", "calories": 120, "notes": "Protein snack"}}
      ],
      "dinner": [
        {{"name": "Multigrain Roti", "quantity": "2 rotis", "calories": 160, "notes": null}},
        {{"name": "Moong Dal", "quantity": "1 katori", "calories": 130, "notes": "Light and easy to digest"}},
        {{"name": "Mixed Vegetable Curry", "quantity": "1 katori", "calories": 100, "notes": null}}
      ],
      "water_intake": "2.5–3 litres throughout the day"
    }}
  ],
  "exercise_plan": [
    {{"name": "Gentle Walking", "duration": "10–15 minutes", "sets_reps": null, "notes": "Start slow, increase gradually", "is_avoid": false}},
    {{"name": "Deep Breathing Exercises", "duration": "5 minutes", "sets_reps": "3 sets", "notes": "Pranayama — helps recovery", "is_avoid": false}},
    {{"name": "Running or Jumping", "duration": "Avoid completely", "sets_reps": null, "notes": "Too stressful during recovery", "is_avoid": true}}
  ],
  "foods_to_avoid": [
    "Fried foods like samosa, pakora",
    "Sugary drinks and cold drinks",
    "Processed foods and fast food",
    "Excess salt and pickles"
  ],
  "foods_to_include": [
    "Haldi (turmeric) milk before bed — anti-inflammatory",
    "Amla or amla juice — rich in Vitamin C",
    "Moong dal khichdi — easy to digest",
    "Fresh seasonal fruits"
  ],
  "general_tips": [
    "Sleep 7–8 hours every night for faster recovery",
    "Eat small meals every 3–4 hours instead of large meals",
    "Avoid stress — practice deep breathing or light meditation",
    "Follow up with your doctor as scheduled"
  ],
  "follow_up": "Visit doctor after 2 weeks or if symptoms worsen"
}}

Create all 7 days with variety. Use different Indian meals each day. Be specific to the patient's condition.
"""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=6000,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.content[0].text.strip()
        raw = re.sub(r"```json\s*", "", raw)
        raw = re.sub(r"```\s*", "", raw)
        raw = raw.strip()

        result = json.loads(raw)
        result["source"] = "ai"
        return result

    except Exception as e:
        print(f"⚠️ AI plan generation failed: {e}")
        return get_fallback_plan(patient_info)


async def extract_report_text(image_base64: str, mime_type: str) -> str:
    """
    Use Claude Vision to extract text from uploaded doctor's report (image or PDF).
    """
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": mime_type, "data": image_base64}
                    },
                    {
                        "type": "text",
                        "text": "Extract all medical information from this doctor's report. Include diagnosis, prescribed medications, restrictions, and doctor's recommendations. Return as plain text summary."
                    }
                ]
            }]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"⚠️ Report extraction failed: {e}")
        return ""


# ─── Fallback Plan ────────────────────────────────────────────────────────────

def get_fallback_plan(patient_info: dict) -> dict:
    """Basic Indian recovery plan when AI is unavailable."""
    food_pref = patient_info.get("food_preference", "veg")
    is_veg = food_pref in ["veg", "eggetarian"]

    breakfast_options = [
        [{"name": "Oats Porridge", "quantity": "1 bowl", "calories": 250, "notes": "Add fruits"}, {"name": "Banana", "quantity": "1", "calories": 90, "notes": None}],
        [{"name": "Idli", "quantity": "3 pieces", "calories": 200, "notes": "With sambar"}, {"name": "Coconut Chutney", "quantity": "2 tbsp", "calories": 60, "notes": None}],
        [{"name": "Poha", "quantity": "1 bowl", "calories": 250, "notes": "Add peanuts for protein"}, {"name": "Green Tea", "quantity": "1 cup", "calories": 5, "notes": None}],
        [{"name": "Moong Dal Cheela", "quantity": "2 pieces", "calories": 220, "notes": "High protein"}, {"name": "Curd", "quantity": "½ bowl", "calories": 60, "notes": None}],
        [{"name": "Upma", "quantity": "1 bowl", "calories": 230, "notes": "Add vegetables"}, {"name": "Buttermilk", "quantity": "1 glass", "calories": 40, "notes": None}],
        [{"name": "Whole Wheat Paratha", "quantity": "2", "calories": 280, "notes": "With less oil"}, {"name": "Curd", "quantity": "1 bowl", "calories": 60, "notes": None}],
        [{"name": "Dalia (Broken Wheat)", "quantity": "1 bowl", "calories": 220, "notes": "With milk or vegetables"}, {"name": "Amla Juice", "quantity": "1 glass", "calories": 30, "notes": "Vitamin C"}],
    ]

    lunch_base = [
        {"name": "Brown Rice / Roti", "quantity": "1 katori rice or 2 rotis", "calories": 200, "notes": None},
        {"name": "Dal", "quantity": "1 katori", "calories": 150, "notes": "Protein rich"},
        {"name": "Sabzi", "quantity": "1 katori", "calories": 80, "notes": "Seasonal vegetables"},
        {"name": "Curd / Raita", "quantity": "1 bowl", "calories": 60, "notes": "Probiotic"},
        {"name": "Salad", "quantity": "1 plate", "calories": 30, "notes": "Cucumber, tomato, carrot"},
    ]

    if not is_veg:
        lunch_base.append({"name": "Grilled Chicken / Fish Curry", "quantity": "1 piece / 1 katori", "calories": 180, "notes": "Lean protein"})

    days = ["Day 1 – Monday", "Day 2 – Tuesday", "Day 3 – Wednesday", "Day 4 – Thursday",
            "Day 5 – Friday", "Day 6 – Saturday", "Day 7 – Sunday"]

    diet_plan = []
    for i, day in enumerate(days):
        diet_plan.append({
            "day": day,
            "breakfast": breakfast_options[i],
            "mid_morning": [{"name": "Seasonal Fruit", "quantity": "1 medium", "calories": 80, "notes": "Apple/Papaya/Guava"}, {"name": "Nuts", "quantity": "5–6 almonds", "calories": 50, "notes": "Soaked overnight"}],
            "lunch": lunch_base,
            "evening_snack": [{"name": "Roasted Chana / Makhana", "quantity": "1 handful", "calories": 100, "notes": "Healthy snack"}, {"name": "Herbal Tea", "quantity": "1 cup", "calories": 5, "notes": "Ginger-tulsi tea"}],
            "dinner": [
                {"name": "Khichdi / Roti", "quantity": "1 bowl khichdi or 2 rotis", "calories": 250, "notes": "Light and nutritious"},
                {"name": "Moong Dal Soup", "quantity": "1 bowl", "calories": 120, "notes": "Easy to digest"},
                {"name": "Steamed Vegetables", "quantity": "1 katori", "calories": 70, "notes": None},
            ],
            "water_intake": "2.5–3 litres throughout the day"
        })

    return {
        "condition": patient_info.get("recovery_goal", "General Recovery"),
        "diet_plan": diet_plan,
        "exercise_plan": [
            {"name": "Gentle Walking", "duration": "10–15 min", "sets_reps": None, "notes": "Start slow, increase by 5 min each week", "is_avoid": False},
            {"name": "Deep Breathing (Pranayama)", "duration": "5–10 min", "sets_reps": "Morning and evening", "notes": "Anulom Vilom helps recovery", "is_avoid": False},
            {"name": "Gentle Stretching", "duration": "5–10 min", "sets_reps": None, "notes": "Avoid painful movements", "is_avoid": False},
            {"name": "Yoga (Gentle poses)", "duration": "15–20 min", "sets_reps": None, "notes": "Child's pose, Cat-Cow, Legs up the wall", "is_avoid": False},
            {"name": "Heavy Weight Lifting", "duration": "Avoid", "sets_reps": None, "notes": "Do not lift heavy weights during recovery", "is_avoid": True},
            {"name": "High Impact Cardio (Running/Jumping)", "duration": "Avoid", "sets_reps": None, "notes": "Too stressful for recovering body", "is_avoid": True},
        ],
        "foods_to_avoid": [
            "Fried foods (samosa, pakora, puri)",
            "Sugary drinks and cold drinks",
            "Processed and packaged foods",
            "Excess salt and pickles (achar)",
            "Alcohol and smoking",
            "Maida-based foods (white bread, biscuits)"
        ],
        "foods_to_include": [
            "Haldi doodh (turmeric milk) before bed — anti-inflammatory",
            "Amla or amla juice — Vitamin C boosts immunity",
            "Moong dal khichdi — easy to digest, nutritious",
            "Adrak-tulsi chai (ginger-tulsi tea) — healing properties",
            "Seasonal fruits especially papaya, banana, pomegranate",
            "Coconut water — hydrating and electrolyte-rich"
        ],
        "general_tips": [
            "Sleep 7–8 hours every night — body heals during sleep",
            "Eat small meals every 3–4 hours rather than 2 large meals",
            "Avoid stress — practice deep breathing or light meditation daily",
            "Take all medications on time as prescribed by doctor",
            "Keep a daily journal of symptoms to share with doctor",
            "Stay in a clean, well-ventilated room"
        ],
        "follow_up": "Visit your doctor after 2 weeks or immediately if symptoms worsen",
        "source": "fallback"
    }