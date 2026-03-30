def build_diet_prompt(name, gender, age, height, weight, goal):
    bmi = weight / ((height / 100) ** 2)

    if goal == "Weight Loss":
        diet_type = "Low carb, high protein, 500 calorie deficit"
    elif goal == "Build Muscle":
        diet_type = "High carb, high protein, 300 calorie surplus"
    else:
        diet_type = "Balanced macros, maintenance calories"

    prompt = f"""
    Act as a professional nutritionist for {name}.
    Stats: Age {age}, Gender {gender}, BMI {bmi:.1f}, Goal: {goal}, Strategy: {diet_type}.
    
    CRITICAL: You MUST ONLY generate menus based strictly on authentic Indian cuisine. Do not include any Western or non-Indian dishes.

    STRICT FORMAT:
    Day 1: Daily Nutrition Plan
    - Meal Name : Time, Calories, Notes

    Day 2: Daily Nutrition Plan
    - Meal Name : Time, Calories, Notes

    Day 3: Daily Nutrition Plan
    - Meal Name : Time, Calories, Notes

    Day 4: Daily Nutrition Plan
    - Meal Name : Time, Calories, Notes

    Day 5: Daily Nutrition Plan
    - Meal Name : Time, Calories, Notes

    Provide 4 unique meals per day. Use the ':' and ',' format exactly as shown above.
    Make each day different with varied meals and calorie counts.
    Do not include any introductory or concluding text.
    """
    return prompt
