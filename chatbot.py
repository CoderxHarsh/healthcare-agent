# import google.generativeai as genai
from langchain_groq import ChatGroq
# Source - https://stackoverflow.com/a/68200726
# Posted by Martin Tovmassian, modified by community. See post 'Timeline' for change history
# Retrieved 2026-04-04, License - CC BY-SA 4.0

import os                                                                                                                                                                                                          
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from tools import get_tool_context

load_dotenv(Path("./.env"))

# Load variables from .env before reading GROK_API_KEY.

api_key = os.getenv("GROK_API_KEY")
if not api_key:
    raise RuntimeError(
        "Missing GROK_API_KEY. Add it to your .env file or environment variables."
    )

# genai.configure(api_key=api_key)

# model = ChatGroq(model="grok-2", temperature=0.5)
model = ChatGroq(
    model = "openai/gpt-oss-20b",
    api_key = api_key,
    temperature =0.7,
    max_tokens = 2048
)
#What is temperature in model selection?
"""0.0 ──────────────────── 1.0 ──────────────────── 2.0
 │                         │                         │
 │                         │                         │
Robotic                 Balanced                  Chaotic
Always picks          Mix of safe +            Very random,
safest answer          creative                unpredictable"""


def get_response(user_input, user_profile=None, health_logs=None):
    # Build a personalized context block from onboarding data
    profile_context = ""
    if user_profile:
        profile_parts = []
        if user_profile.get("name"):
            profile_parts.append(f"Name: {user_profile['name']}")
        if user_profile.get("age"):
            profile_parts.append(f"Age: {user_profile['age']}")
        if user_profile.get("gender"):
            profile_parts.append(f"Gender: {user_profile['gender']}")
        if user_profile.get("height_cm"):
            profile_parts.append(f"Height: {user_profile['height_cm']} cm")
        if user_profile.get("weight_kg"):
            profile_parts.append(f"Weight: {user_profile['weight_kg']} kg")
        if user_profile.get("health_conditions"):
            profile_parts.append(f"Health Conditions: {user_profile['health_conditions']}")
        if user_profile.get("medications"):
            profile_parts.append(f"Current Medications: {user_profile['medications']}")
        if user_profile.get("allergies"):
            profile_parts.append(f"Allergies: {user_profile['allergies']}")
        if user_profile.get("fitness_level"):
            profile_parts.append(f"Fitness Level: {user_profile['fitness_level']}")
        if user_profile.get("health_goals"):
            profile_parts.append(f"Health Goals: {user_profile['health_goals']}")

        if profile_parts:
            profile_context = (
                "\n\n--- USER HEALTH PROFILE ---\n"
                + "\n".join(profile_parts)
                + "\n--- END PROFILE ---\n\n"
                "USE the above health profile to personalize your advice. "
                "Consider the user's age, weight, conditions, medications, "
                "allergies, fitness level, and goals when answering. "
                "Do NOT repeat the profile back unless the user asks about it.\n"
            )

    # Build health logs context from recent tracked data
    logs_context = ""
    if health_logs:
        log_lines = []
        for log in health_logs[:20]:  # Limit to 20 most recent to avoid token overflow
            metric = log.get("metric_type", "").replace("_", " ").title()
            value = log.get("value", "")
            unit = log.get("unit", "")
            date = log.get("created_at", "")[:16]  # Trim to YYYY-MM-DDTHH:MM
            notes = log.get("notes", "")
            entry = f"  • {date} | {metric}: {value} {unit}"
            if notes:
                entry += f" (Note: {notes})"
            log_lines.append(entry)

        if log_lines:
            logs_context = (
                "\n\n--- RECENT HEALTH LOGS (last 30 days) ---\n"
                + "\n".join(log_lines)
                + "\n--- END LOGS ---\n\n"
                "USE the above health logs to understand the user's recent health trends. "
                "Reference specific readings when relevant (e.g. 'your last BP was 130/85'). "
                "Spot trends (improving, worsening, stable) and mention them. "
                "Do NOT dump the entire log back unless the user asks to see it.\n"
            )

    # --- TOOL ROUTING ---
    # Detect the topic and get specialized tool context
    tool_context, tool_name = get_tool_context(user_input, user_profile)

    prompt = f"""
    You are a helpful health assistant.
    {profile_context}
    {logs_context}
    {tool_context}

    -You are a certified healthcare assistant.
    -ONLY answer based on the provided context.
    -If unsure, say "consult a doctor".
    -Never guess medications or dosages.
    -Answer clearly and safely.
    -Try to be concise and supportive.
    -Don't give long explanations.
    -Avoid giving dangerous medical advice.
    -If serious issue → suggest doctor consultation.
    -Ask follow-up questions if user input is vague.
    -Ask clarifying questions if needed and store the answers in the conversation history.
    -Ask for more details if user input is vague.
    -Dont start a conversation with new words that define the situation of the user, 
    always tell about the situation and then use the coined word for it.
    -If user mentions a health metric (e.g. blood pressure, sugar level, weight),
    try to extract and save it, but don't ask for it directly.
    -When the user has health conditions or medications listed in their profile,
    factor those into your recommendations (e.g. avoid suggesting exercises 
    that conflict with their conditions, warn about drug interactions, etc.)

    User: {user_input}
    """

    response = model.invoke(prompt)

    # Prepend a small tool badge if a specialized tool was used
    result = response.text
    if tool_name != "general":
        result = f"*{tool_name}*\n\n{result}"

    return result