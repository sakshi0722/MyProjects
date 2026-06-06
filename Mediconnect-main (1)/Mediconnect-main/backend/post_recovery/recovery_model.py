from pydantic import BaseModel
from typing import Optional, List


class PatientInfo(BaseModel):
    user_id: str
    name: str
    age: int
    gender: str                          # male / female / other
    weight_kg: float
    height_cm: float
    food_preference: str                 # veg / non-veg / eggetarian
    allergies: Optional[List[str]] = []
    health_conditions: Optional[List[str]] = []   # diabetes, hypertension, etc.
    current_medications: Optional[List[str]] = []
    activity_level: str                  # sedentary / light / moderate / active
    recovery_goal: Optional[str] = ""    # e.g. "recover from knee surgery"
    report_summary: Optional[str] = ""  # extracted from uploaded PDF/image


class MealItem(BaseModel):
    name: str
    quantity: str
    calories: Optional[int] = None
    notes: Optional[str] = None


class DayMealPlan(BaseModel):
    day: str
    breakfast: List[MealItem]
    mid_morning: List[MealItem]
    lunch: List[MealItem]
    evening_snack: List[MealItem]
    dinner: List[MealItem]
    water_intake: str


class ExerciseItem(BaseModel):
    name: str
    duration: str
    sets_reps: Optional[str] = None
    notes: Optional[str] = None
    is_avoid: bool = False              # exercises to AVOID during recovery


class RecoveryPlan(BaseModel):
    user_id: str
    patient_info: PatientInfo
    condition: str
    diet_plan: List[DayMealPlan]
    exercise_plan: List[ExerciseItem]
    foods_to_avoid: List[str]
    foods_to_include: List[str]
    general_tips: List[str]
    follow_up: str