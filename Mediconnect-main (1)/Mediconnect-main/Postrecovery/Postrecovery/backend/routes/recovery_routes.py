from flask import Blueprint, request, jsonify
from backend.services.calorie_service import calculate_bmr, calculate_tdee
from backend.services.diet_service import recommend_diet
from backend.services.exercise_service import recommend_exercise
from backend.models.recovery_model import predict_recovery
from backend.database.db_connection import save_data

recovery_bp = Blueprint("recovery", __name__)

@recovery_bp.route("/post_recovery", methods=["POST"])
def post_recovery():
    data = request.json

    age = data["age"]
    weight = data["weight"]
    height = data["height"]
    gender = data["gender"]
    activity = data["activity"]
    injury = data["injury"]
    goal = data["goal"]
    severity = data["severity"]

    bmr = calculate_bmr(age, weight, height, gender)
    tdee = calculate_tdee(bmr, activity)

    diet = recommend_diet(tdee, goal)
    exercise = recommend_exercise(injury)
    recovery_days = predict_recovery(age, severity)

    response = {
        "diet_plan": diet,
        "exercise_plan": exercise,
        "estimated_recovery_days": recovery_days
    }

    save_data(response)

    return jsonify(response)
