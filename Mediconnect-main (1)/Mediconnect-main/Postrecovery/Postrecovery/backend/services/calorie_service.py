def calculate_bmr(age, weight, height, gender):
    if gender.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161


def calculate_tdee(bmr, activity_level):
    activity_multipliers = {
        "low": 1.2,
        "moderate": 1.55,
        "high": 1.9
    }
    return bmr * activity_multipliers.get(activity_level, 1.2)
