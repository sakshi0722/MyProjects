def recommend_exercise(injury_type):
    plans = {
        "fracture": "Light physiotherapy & stretching",
        "knee": "Cycling & quad strengthening",
        "back": "Core strengthening & yoga",
        "burn": "Light mobility exercises"
    }

    return plans.get(injury_type, "General walking 30 mins")
