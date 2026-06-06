from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/post_recovery", methods=["POST"])
def post_recovery():

    # ---- Get Form Data (Matching index.html exactly) ----
    name = request.form.get("name")
    age = int(request.form.get("age"))
    weight = float(request.form.get("weight"))
    height = float(request.form.get("height"))
    gender = request.form.get("gender")
    injury = request.form.get("injury")
    severity = request.form.get("severity")
    activity = request.form.get("activity")
    sleep = request.form.get("sleep")
    diet_pref = request.form.get("diet_pref")

    # ---- BMR Calculation ----
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # ---- Activity Multiplier ----
    activity_levels = {
        "no exercise": 1.2,
        "moderate": 1.55,
        "high": 1.75
    }

    tdee = bmr * activity_levels.get(activity, 1.2)

    # ---- Simple Recovery Logic ----
    severity_factor = {
        "mild": 5,
        "moderate": 10,
        "severe": 20
    }

    recovery_time = age + severity_factor.get(severity, 5)

    # ---- Exercise Suggestion ----
    exercise_plan = {
        "knee_strain": "Light walking and leg strengthening exercises",
        "back_strain": "Stretching and core strengthening exercises",
        "ankle_sprain": "Ankle mobility and balance exercises",
        "wrist_sprain": "Wrist rotation and grip exercises",
        "hairline_fracture": "Physiotherapy and gradual movement",
        "shoulder_pain": "Shoulder mobility and resistance band exercises",
        "neck_strain": "Neck stretching and posture correction exercises",
        "minor_burn": "Light flexibility exercises",
        "elbow_injury": "Forearm strengthening exercises",
        "muscle_pull": "Gentle stretching and light activity"
    }

    exercise = exercise_plan.get(injury, "Regular walking")

    # ---- Diet Plan ----
    diet_plan = f"{diet_pref} diet with high protein and balanced nutrition."

    # ---- Progress (Dummy Example) ----
    progress = 50

    return render_template("index.html",
                           result=True,
                           name=name,
                           calories=round(tdee),
                           diet=diet_plan,
                           exercise=exercise,
                           recovery=recovery_time,
                           progress=progress)


if __name__ == "__main__":
    app.run(debug=True)
