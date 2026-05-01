# import google.generativeai as genai
from langchain_groq import ChatGroq
# Source - https://stackoverflow.com/a/68200726
# Posted by Martin Tovmassian, modified by community. See post 'Timeline' for change history
# Retrieved 2026-04-04, License - CC BY-SA 4.0

import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from .tools import get_tool_context
#for medical info retrieval from medlineplus api
from .medlineplus import get_medical_info
# RAG pipeline — retrieve grounded knowledge from the vector store
from .rag.retriever import retrieve, format_rag_context

# Load .env from root directory (works from any location)
env_path = find_dotenv() or Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

import re
#for cleaning html tags from medlineplus summaries
def clean_html(text):
    clean = re.sub('<.*?>', '', text)
    return clean
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
    temperature =0.6,
    max_tokens = 2048
)
#What is temperature in model selection?
"""0.0 ──────────────────── 1.0 ──────────────────── 2.0
 │                         │                         │
 │                         │                         │
Robotic                 Balanced                  Chaotic
Always picks          Mix of safe +            Very random,
safest answer          creative                unpredictable"""
def get_response(user_input, user_profile=None, health_logs=None, chat_history=None):

    # --- BUILD CONVERSATION HISTORY ---
    # Include recent messages so the LLM has context for follow-up questions
    history_context = ""
    if chat_history:
        # Keep last 10 messages (5 exchanges) to stay within token limits
        recent = chat_history[-10:]
        history_lines = []
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            # Truncate very long messages to save tokens
            content = msg["content"][:500]
            history_lines.append(f"{role}: {content}")

        if history_lines:
            history_context = (
                "\n\n--- CONVERSATION HISTORY ---\n"
                + "\n".join(history_lines)
                + "\n--- END HISTORY ---\n\n"
                "The above is the recent conversation. Use it to understand context. "
                "The user's latest message below may be a follow-up to this conversation.\n"
            )

    # -------------------------------
    # 🧠 STEP 1: Try MedlinePlus FIRST
    # -------------------------------
    medical_keywords = ["what is", "symptoms", "disease", "treatment", "condition"]

    if any(word in user_input.lower() for word in medical_keywords):
        med_data = get_medical_info(user_input)

        if med_data:
            clean_text = clean_html(med_data['summary'])
            prompt = f"""Explain the following medical information in simple clear terms.
            keep it :
            - Short (5-6 lines)
            - easy to understand (avoid medical jargon)
            - actionable (what can the user do with this info)
            - safe (avoid giving dangerous advice)
            - Present answer in well formatted bullet points if possible.

            Medicinal Info:
            {clean_text}
            {history_context}

            User Question: {user_input}
            """
            response = model.invoke(prompt)
            return f"""{response.content}\n
            Source: MedlinePlus (https://medlineplus.gov/)
            Disclaimer: This information is for educational purposes only. Consult a healthcare professional for personalized medical advice."""


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

    # (Conversation history generation moved to the top)

    # --- RAG RETRIEVAL ---
    # Fetch the most relevant chunks from the local knowledge base (PostgreSQL)
    user_id = user_profile.get("id") if user_profile else None
    rag_chunks = retrieve(user_input, user_id=user_id)
    rag_context = format_rag_context(rag_chunks)

    # --- TOOL ROUTING (history-aware) ---
    # Detect the topic from the current message AND recent history
    tool_context, tool_name = get_tool_context(user_input, user_profile, chat_history)

    # Build a guest-mode hint when no profile is available
    guest_hint = ""
    if not user_profile:
        guest_hint = (
            "\n⚠️ GUEST MODE: The user has NO profile. "
            "Do NOT ask for their name, age, weight, conditions, medications, or any personal info. "
            "Provide helpful general advice based ONLY on what the user said.\n"
        )

    prompt = f"""
    ⛔ HIGHEST-PRIORITY RULES (NEVER BREAK THESE — OVERRIDE EVERYTHING ELSE):
    - NEVER ask ANY questions. Not about details, severity, duration, symptoms, history, or anything.
    - NEVER write "Could you tell me...", "Can you share...", "What is your...", "Tell me about...", "Do you have..." or ANY request for information.
    - NEVER list questions for the user to answer.
    - NEVER suggest the user provide more details.
    - ANSWER DIRECTLY AND IMMEDIATELY based on the user's input, profile, and conversation history.
    - Make reasonable assumptions where needed and state them briefly.
    {guest_hint}
    You are a helpful, certified healthcare assistant.
    {profile_context}
    {logs_context}
    {history_context}
    {rag_context}
    {tool_context}

    GENERAL GUIDELINES:
    - Prioritize information from the KNOWLEDGE BASE section above when answering.
    - If unsure, say "consult a doctor".
    - Never guess medications or dosages.
    - Answer clearly and safely.
    - Try to be concise and supportive.
    - Don't give long explanations.
    - Avoid giving dangerous medical advice.
    - If serious issue → suggest doctor consultation.
    - Don't start a conversation with new words that define the situation of the user,
      always tell about the situation and then use the coined word for it.
    - If user mentions a health metric (e.g. blood pressure, sugar level, weight),
      acknowledge it naturally but do not request additional metrics.
    - When the user has health conditions or medications listed in their profile,
      factor those into your recommendations (e.g. avoid suggesting exercises
      that conflict with their conditions, warn about drug interactions, etc.)

    User: {user_input}
    """

    response = model.invoke(prompt)

    # Prepend a small tool badge if a specialized tool was used
    result = response.content
    if tool_name != "general":
        result = f"*{tool_name}*\n\n{result}"

    return result