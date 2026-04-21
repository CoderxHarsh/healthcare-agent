"""
Healthcare AI Tools Module
--------------------------
Provides 5 specialized tool functions for the chatbot:
  1. Fitness    – workout/exercise recommendations
  2. Medication – drug info, interaction warnings
  3. Nutrition  – dietary advice, meal suggestions
  4. Medical Research – evidence-based health info
  5. Symptoms   – symptom triage & assessment

Each tool returns a context string that gets injected into the LLM prompt
so responses are domain-specific and personalized.
"""

import re
import math
from typing import Optional, Dict, Tuple


# ============================================
# GLOBAL BEHAVIOR RULES (injected into every tool)
# ============================================

GLOBAL_BEHAVIOR_RULES = [
    "",
    "⚠️ GLOBAL BEHAVIOR RULES (HIGHEST PRIORITY — ALWAYS FOLLOW):",
    "- NEVER ask ANY questions. Do NOT ask clarifying, follow-up, or probing questions.",
    "- NEVER say 'Could you tell me...', 'What is your...', 'Do you have...', or similar.",
    "- NEVER request the user to provide more information, details, or context.",
    "- If profile data is missing, silently assume reasonable defaults and proceed.",
    "- Do not mention that profile data is missing or unavailable.",
    "- Give a complete, structured answer immediately based ONLY on what the user said.",
    "- Keep responses concise, actionable, and easy to read.",
]


# ============================================
# HELPER: BMI + Caloric Calculations
# ============================================

def calculate_bmi(weight_kg: float, height_cm: float) -> Tuple[float, str]:
    """Calculate BMI and return (value, category)"""
    if not weight_kg or not height_cm or height_cm == 0:
        return (0.0, "unknown")
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return (bmi, category)


def estimate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Estimate Basal Metabolic Rate using Mifflin-St Jeor equation"""
    if not all([weight_kg, height_cm, age]):
        return 0.0
    if gender and gender.lower() == "female":
        return round(10 * weight_kg + 6.25 * height_cm - 5 * age - 161)
    return round(10 * weight_kg + 6.25 * height_cm - 5 * age + 5)


def estimate_tdee(bmr: float, fitness_level: str) -> float:
    """Estimate Total Daily Energy Expenditure"""
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very active": 1.9,
    }
    mult = multipliers.get((fitness_level or "").lower(), 1.4)
    return round(bmr * mult)


# ============================================
# TOPIC DETECTION (keyword-based router)
# ============================================

TOPIC_PATTERNS = {
    "fitness": re.compile(
        r"\b(exercise|workout|gym|cardio|strength|stretch|yoga|run|running|jog|"
        r"walk|walking|squat|pushup|push-up|pull-up|plank|training|hiit|"
        r"muscle|flexibility|endurance|steps|active|sedentary|"
        r"warm.?up|cool.?down|reps|sets|fitness|treadmill|cycling|swim)\b",
        re.IGNORECASE
    ),
    "medication": re.compile(
        r"\b(medicine|medication|drug|pill|tablet|capsule|dose|dosage|"
        r"prescription|otc|over.the.counter|antibiotic|painkiller|"
        r"ibuprofen|paracetamol|acetaminophen|aspirin|metformin|"
        r"side.?effect|interaction|pharmacy|supplement|vitamin|"
        r"insulin|statin|antidepressant|inhaler)\b",
        re.IGNORECASE
    ),
    "nutrition": re.compile(
        r"\b(diet|nutrition|food|eat|eating|meal|calorie|protein|carb|fat|"
        r"fiber|vitamin|mineral|fruit|vegetable|sugar|sodium|cholesterol|"
        r"breakfast|lunch|dinner|snack|recipe|cook|healthy.?eating|"
        r"keto|vegan|vegetarian|fasting|intermittent|macro|hydration|water)\b",
        re.IGNORECASE
    ),
    "medical_research": re.compile(
        r"\b(research|study|studies|clinical|trial|evidence|journal|"
        r"published|findings|data|statistics|prevalence|guidelines|"
        r"WHO|CDC|NIH|FDA|recommended|latest|medical.?science|"
        r"peer.?review|systematic|meta.?analysis|cause|risk.?factor)\b",
        re.IGNORECASE
    ),
    "symptoms": re.compile(
        r"\b(symptom|pain|ache|headache|migraine|fever|cough|cold|flu|"
        r"nausea|vomit|diarrhea|dizzy|dizziness|fatigue|tired|"
        r"sore|throat|chest|stomach|cramp|rash|itch|swelling|"
        r"breathless|shortness.?of.?breath|numbness|tingling|"
        r"bleeding|burning|inflammation|infection|diagnosis)\b",
        re.IGNORECASE
    ),
}


def detect_topic(user_input: str) -> str:
    """
    Detect which healthcare domain the user's query falls into.
    Returns the topic key or 'general' if no specific match.
    """
    scores = {}
    for topic, pattern in TOPIC_PATTERNS.items():
        matches = pattern.findall(user_input)
        scores[topic] = len(matches)

    if not scores or max(scores.values()) == 0:
        return "general"

    return max(scores, key=scores.get)


# ============================================
# TOOL FUNCTIONS
# ============================================

def fitness_tool(user_input: str, profile: Optional[Dict] = None) -> str:
    """Generate fitness-specific context for the LLM prompt"""
    context_parts = [
        "🏋️ ACTIVE TOOL: FITNESS ADVISOR",
        "You are now acting as a certified fitness advisor.",
        "Provide safe, personalized exercise recommendations.",
        "Answer directly without asking follow-up questions.",
    ]

    if profile:
        weight = profile.get("weight_kg")
        height = profile.get("height_cm")
        age = profile.get("age")
        gender = profile.get("gender")
        conditions = profile.get("health_conditions", "")
        fitness_level = profile.get("fitness_level", "")
        goals = profile.get("health_goals", "")

        if weight and height:
            bmi, bmi_cat = calculate_bmi(weight, height)
            context_parts.append(f"User's BMI: {bmi} ({bmi_cat})")

        if fitness_level:
            context_parts.append(f"Current fitness level: {fitness_level}")
            intensity_map = {
                "sedentary": "Start with very gentle, low-impact exercises. 10-15 min sessions.",
                "light": "Recommend light to moderate exercises. 20-30 min sessions.",
                "moderate": "Can handle moderate intensity. 30-45 min sessions.",
                "active": "Ready for challenging workouts. 45-60 min sessions.",
                "very active": "Can handle high-intensity training. 60+ min sessions.",
            }
            advice = intensity_map.get(fitness_level.lower(), "")
            if advice:
                context_parts.append(f"Intensity guidance: {advice}")

        if conditions:
            context_parts.append(
                f"⚠️ SAFETY: User has these conditions: {conditions}. "
                "Avoid exercises that could worsen them. Suggest safe alternatives."
            )

        if goals:
            context_parts.append(f"User's goals: {goals}. Tailor exercises toward these goals.")

    else:
        context_parts.append(
            "No profile available. Assume a moderately healthy adult. "
            "Provide general beginner-to-intermediate recommendations. "
            "Do NOT ask the user for their profile, age, fitness level, or any personal details."
        )

    context_parts.extend([
        "",
        "RULES:",
        "- Always include warm-up and cool-down recommendations.",
        "- Specify sets, reps, and duration where applicable.",
        "- Warn about any exercise that conflicts with user's health conditions.",
        "- Suggest progression levels (beginner → intermediate → advanced).",
        "- Recommend rest days and recovery practices.",
    ])

    context_parts.extend(GLOBAL_BEHAVIOR_RULES)
    return "\n".join(context_parts)


def medication_tool(user_input: str, profile: Optional[Dict] = None) -> str:
    """Generate medication-specific context for the LLM prompt"""
    context_parts = [
        "💊 ACTIVE TOOL: MEDICATION ADVISOR",
        "You are now acting as a medication information assistant.",
        "Provide factual drug information but NEVER prescribe or change dosages.",
        "Answer directly without asking follow-up questions.",
    ]

    if profile:
        current_meds = profile.get("medications", "")
        allergies = profile.get("allergies", "")
        conditions = profile.get("health_conditions", "")

        if current_meds:
            context_parts.append(
                f"⚠️ User's CURRENT MEDICATIONS: {current_meds}. "
                "Check for potential drug interactions with anything discussed."
            )

        if allergies:
            context_parts.append(
                f"🚨 User's ALLERGIES: {allergies}. "
                "NEVER suggest medications that could trigger these allergies."
            )

        if conditions:
            context_parts.append(
                f"User's conditions: {conditions}. "
                "Consider contraindications for these conditions."
            )

    else:
        context_parts.append(
            "No profile available. Provide general medication information. "
            "Assume no known allergies or interactions. "
            "Do NOT ask the user for their medication list, allergies, or any personal details."
        )

    context_parts.extend([
        "",
        "RULES:",
        "- NEVER prescribe medications or suggest specific dosages.",
        "- Always say 'consult your doctor or pharmacist' for dosage questions.",
        "- Mention common side effects when discussing any medication.",
        "- Flag potential interactions with the user's current medications.",
        "- Distinguish between OTC and prescription medications.",
        "- If the user asks about changing/stopping medication, strongly advise consulting their doctor.",
    ])

    context_parts.extend(GLOBAL_BEHAVIOR_RULES)
    return "\n".join(context_parts)


def nutrition_tool(user_input: str, profile: Optional[Dict] = None) -> str:
    """Generate nutrition-specific context for the LLM prompt"""
    context_parts = [
        "🥗 ACTIVE TOOL: NUTRITION ADVISOR",
        "You are now acting as a certified nutrition advisor.",
        "Provide dietary advice tailored to the user's profile and goals.",
        "Answer directly without asking follow-up questions.",
    ]

    if profile:
        weight = profile.get("weight_kg")
        height = profile.get("height_cm")
        age = profile.get("age")
        gender = profile.get("gender")
        fitness_level = profile.get("fitness_level", "")
        goals = profile.get("health_goals", "")
        conditions = profile.get("health_conditions", "")
        allergies = profile.get("allergies", "")

        if weight and height:
            bmi, bmi_cat = calculate_bmi(weight, height)
            context_parts.append(f"User's BMI: {bmi} ({bmi_cat})")

        if all([weight, height, age]):
            bmr = estimate_bmr(weight, height, age, gender)
            tdee = estimate_tdee(bmr, fitness_level)
            context_parts.append(f"Estimated daily caloric need (TDEE): ~{tdee} kcal/day")

            if goals:
                if "weight loss" in goals.lower():
                    deficit = tdee - 500
                    context_parts.append(
                        f"For weight loss: recommend ~{deficit} kcal/day (500 kcal deficit)."
                    )
                elif "weight gain" in goals.lower():
                    surplus = tdee + 300
                    context_parts.append(
                        f"For weight gain: recommend ~{surplus} kcal/day (300 kcal surplus)."
                    )

        if conditions:
            context_parts.append(
                f"⚠️ User's conditions: {conditions}. "
                "Adjust dietary advice accordingly (e.g., low-sodium for hypertension, "
                "low-sugar for diabetes, anti-inflammatory for arthritis)."
            )

        if allergies:
            context_parts.append(
                f"🚨 User's ALLERGIES: {allergies}. "
                "NEVER suggest foods that contain these allergens."
            )

        if goals:
            context_parts.append(f"User's goals: {goals}. Align meal suggestions with these goals.")

    else:
        context_parts.append(
            "No profile available. Assume a moderately active adult (~2000 kcal/day) with no known conditions. "
            "Provide general balanced nutrition advice. "
            "Do NOT ask the user for their weight, age, diet preferences, or any personal details."
        )

    context_parts.extend([
        "",
        "RULES:",
        "- Suggest specific meal ideas with approximate macro breakdowns when helpful.",
        "- Consider cultural diversity in food suggestions.",
        "- Mention portion sizes and meal timing.",
        "- Highlight foods to avoid based on the user's conditions and allergies.",
        "- Recommend hydration (water intake based on weight: ~30ml per kg body weight).",
        "- If the user has diabetes, always consider glycemic index.",
    ])

    context_parts.extend(GLOBAL_BEHAVIOR_RULES)
    return "\n".join(context_parts)


def medical_research_tool(user_input: str, profile: Optional[Dict] = None) -> str:
    """Generate medical-research-specific context for the LLM prompt"""
    context_parts = [
        "🔬 ACTIVE TOOL: MEDICAL RESEARCH ADVISOR",
        "You are now acting as a medical research information assistant.",
        "Provide evidence-based, factual health information from established guidelines.",
        "Answer directly without asking follow-up questions.",
    ]

    if profile:
        conditions = profile.get("health_conditions", "")
        age = profile.get("age")
        gender = profile.get("gender")

        if conditions:
            context_parts.append(
                f"User's conditions: {conditions}. "
                "Prioritize research and guidelines relevant to these conditions."
            )

        if age:
            context_parts.append(f"User's age: {age}. Consider age-specific guidelines and risk factors.")

        if gender:
            context_parts.append(f"User's gender: {gender}. Consider gender-specific health research.")

    else:
        context_parts.append(
            "No profile available. Provide general population-level research and guidelines. "
            "Do NOT ask the user for their medical history or personal details."
        )

    context_parts.extend([
        "",
        "RULES:",
        "- Cite well-known health organizations (WHO, CDC, NIH, AHA) where relevant.",
        "- Distinguish between established science and emerging/preliminary research.",
        "- Use simple language to explain complex medical concepts.",
        "- Mention when evidence is inconclusive or debated.",
        "- Always note that research findings are general and may not apply to individual cases.",
        "- Recommend consulting a healthcare provider for personal medical decisions.",
        "- If asked about very recent research, clarify that your knowledge has a cutoff date.",
    ])

    context_parts.extend(GLOBAL_BEHAVIOR_RULES)
    return "\n".join(context_parts)


def symptoms_tool(user_input: str, profile: Optional[Dict] = None) -> str:
    """Generate symptom-assessment-specific context for the LLM prompt"""
    context_parts = [
        "🩺 ACTIVE TOOL: SYMPTOM CHECKER",
        "You are a symptom assessment assistant. Your job is to IMMEDIATELY provide a symptom assessment.",
        "",
        "⛔ ABSOLUTE RULES (DO NOT VIOLATE UNDER ANY CIRCUMSTANCE):",
        "- DO NOT ask ANY questions whatsoever. NOT ONE QUESTION.",
        "- DO NOT ask about severity, duration, or other symptoms.",
        "- DO NOT ask clarifying questions.",
        "- DO NOT ask for more details.",
        "- DO NOT suggest the user tell you more information.",
        "- Provide your COMPLETE assessment based ONLY on what the user already told you.",
        "- Assume moderate severity and recent onset. Give the full assessment immediately.",
        "",
    ]

    if profile:
        age = profile.get("age")
        gender = profile.get("gender")
        conditions = profile.get("health_conditions", "")
        medications = profile.get("medications", "")

        if age:
            context_parts.append(f"User age: {age} — consider age-related factors.")

        if gender:
            context_parts.append(f"User gender: {gender} — consider gender-specific factors.")

        if conditions:
            context_parts.append(
                f"EXISTING CONDITIONS: {conditions} — flag any concerning overlaps with reported symptoms."
            )

        if medications:
            context_parts.append(
                f"MEDICATIONS: {medications} — note if symptoms could be side effects."
            )
        context_parts.append("")

    context_parts.extend([
        "OUTPUT FORMAT (follow exactly):",
        "1. Possible causes (most likely first)",
        "2. Urgency: 🟢 Mild / 🟡 Moderate / 🔴 Urgent",
        "3. Recommended next steps",
        "4. Warning signs requiring emergency care",
        "",
        "REMEMBER: You are PROVIDING AN ASSESSMENT, not gathering information.",
        "The user gave you enough information. Analyze it and respond NOW.",
    ])

    context_parts.extend(GLOBAL_BEHAVIOR_RULES)
    return "\n".join(context_parts)


# ============================================
# TOOL REGISTRY
# ============================================

TOOLS = {
    "fitness": {
        "function": fitness_tool,
        "name": "Fitness Advisor",
        "emoji": "🏋️",
    },
    "medication": {
        "function": medication_tool,
        "name": "Medication Advisor",
        "emoji": "💊",
    },
    "nutrition": {
        "function": nutrition_tool,
        "name": "Nutrition Advisor",
        "emoji": "🥗",
    },
    "medical_research": {
        "function": medical_research_tool,
        "name": "Medical Research",
        "emoji": "🔬",
    },
    "symptoms": {
        "function": symptoms_tool,
        "name": "Symptom Checker",
        "emoji": "🩺",
    },
}


def get_tool_context(user_input: str, profile: Optional[Dict] = None, chat_history=None) -> Tuple[str, str]:
    """
    Detect the topic and run the appropriate tool.
    Uses conversation history to maintain tool continuity for follow-up messages.

    Returns:
        (tool_context, tool_name) - the enriched context string and which tool was used.
        tool_name is 'general' if no specific tool matched.
    """
    topic = detect_topic(user_input)
    is_followup = False

    # --- HISTORY-AWARE ROUTING ---
    # If the current message has a weak match (0-1 keyword hits), check whether
    # the recent conversation was using a specific tool and stick with it.
    if chat_history and len(chat_history) >= 2:
        # Count how strong the current match is
        current_scores = {}
        for t, pattern in TOPIC_PATTERNS.items():
            current_scores[t] = len(pattern.findall(user_input))
        current_max = max(current_scores.values()) if current_scores else 0

        # Only override if the current match is weak (0 or 1 keyword)
        if current_max <= 1:
            # Look at recent USER messages to find the dominant topic
            recent_user_msgs = [
                m["content"] for m in chat_history[-6:]
                if m["role"] == "user"
            ]
            if recent_user_msgs:
                combined_history = " ".join(recent_user_msgs)
                history_topic = detect_topic(combined_history)

                # If the conversation history has a clear topic, use it
                if history_topic != "general":
                    topic = history_topic
                    is_followup = True

    if topic == "general":
        return ("", "general")

    tool_info = TOOLS[topic]
    tool_name = f"{tool_info['emoji']} {tool_info['name']}"

    if is_followup:
        # --- FOLLOW-UP MODE ---
        # Don't inject the full rigid tool template (which forces a complete
        # assessment). Instead, give a lightweight prompt so the LLM answers
        # the specific follow-up question naturally using conversation context.
        followup_context_parts = [
            f"{tool_info['emoji']} ACTIVE TOOL: {tool_info['name'].upper()} (FOLLOW-UP MODE)",
            "",
            "The user is asking a FOLLOW-UP question related to the ongoing conversation.",
            "ANSWER THEIR SPECIFIC QUESTION directly, concisely, and naturally.",
            "Do NOT repeat a full assessment or re-diagnose from scratch.",
            "Reference the conversation history to give a contextual answer.",
            "Keep it short and helpful — the user already has the initial assessment.",
        ]
        followup_context_parts.extend(GLOBAL_BEHAVIOR_RULES)
        return ("\n".join(followup_context_parts), tool_name)

    # --- FULL MODE ---
    # First message on this topic — run the complete tool template
    tool_fn = tool_info["function"]
    tool_context = tool_fn(user_input, profile)

    return (tool_context, tool_name)