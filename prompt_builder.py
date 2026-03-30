def calculate_bmi(weight, height):
    height_m = height / 100
    return weight / (height_m ** 2)

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight", "#3498db"
    elif bmi < 25:
        return "Normal Weight", "#2ecc71"
    elif bmi < 30:
        return "Overweight", "#f1c40f"
    else:
        return "Obese", "#e74c3c"

def build_prompt(name, gender, age, height, weight, goal, fitness_level, equipment):
    bmi = calculate_bmi(weight, height)
    bmi_status, status_color = bmi_category(bmi)
    equipment_list = ", ".join(equipment) if equipment else "No Equipment"

    # Create specific instructions for equipment usage
    equipment_instruction = ""
    if equipment and len(equipment) > 1:
        equipment_instruction = f"""
CRITICAL: Use ALL equipment types ({equipment_list}) across the 5 days.
- Day 1: Focus on {equipment[0] if len(equipment) > 0 else 'primary equipment'}
- Day 2: Focus on {equipment[1] if len(equipment) > 1 else 'secondary equipment'}
- Day 4: Focus on {equipment[2] if len(equipment) > 2 else 'additional equipment'}
- Day 5: Combine multiple equipment types
- Include at least 2 exercises per equipment type selected"""

    prompt = f"""You are a professional trainer. Create a 5-day plan for {name}.
User Profile: Age {age}, Gender {gender}, BMI {bmi:.2f}, Goal {goal}, Level {fitness_level}, Equipment {equipment_list}.

{equipment_instruction}

STRICT FORMATTING RULES:
1. Label days as Day 1:, Day 2:, etc.
2. For EVERY exercise, use this EXACT format:
   - Exercise Name | Sets | Reps | Rest
3. Example: - Dumbbell Bench Press | 3 | 10-12 | 60s
4. Day 3 must be "Rest Day".
5. Include exercises using: {equipment_list}
6. Do not include any intro or outro text. Output only the days and exercises."""

    return prompt, bmi, bmi_status, status_color

def build_adjustment_prompt(current_plan, feedback):
    """Generates a prompt to adjust the workout plan based on daily check-in feedback."""
    return f"""You are a professional fitness AI coach. 
The user has provided a daily check-in regarding their body condition and fatigue: "{feedback}"

Here is their current 5-day workout plan:
{current_plan}

Based ONLY on their check-in feedback, critically adapt their plan to keep them safe but progressing.
- If they are sore, swap the sore muscle group for active recovery, stretching, or a different muscle group.
- If they are tired/slept poorly, reduce the volume (sets/reps) or intensity for the upcoming days.
- If they say it's too easy, increase volume or intensity.
- KEEP THE EXACT SAME STRICT FORMATTING RULES AS THE ORIGINAL PLAN:
  1. Label days as Day 1:, Day 2:, etc.
  2. For EVERY exercise, use this EXACT format:
     - Exercise Name | Sets | Reps | Rest
  3. Example: - Dumbbell Bench Press | 3 | 10-12 | 60s
  4. Do not include any intro or outro text. Output only the days and exercises."""
