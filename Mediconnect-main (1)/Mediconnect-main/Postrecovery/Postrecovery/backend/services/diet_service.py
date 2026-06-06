def recommend_diet(tdee, goal):
    if goal == "loss":
        calories = tdee - 500
    elif goal == "gain":
        calories = tdee + 500
    else:
        calories = tdee

    return {
        "recommended_calories": int(calories),
        "protein": "High protein (paneer, eggs, dal)",
        "carbs": "Complex carbs (brown rice, oats)",
        "fats": "Healthy fats (nuts, seeds)"
    }
