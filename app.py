import streamlit as st
from chatbot import get_response
import jwt

st.title("🏥 Your Health Chatbot")

# -------------------------
# SESSION SETUP
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user" not in st.session_state:
    st.session_state.user = None


# -------------------------
# CHECK LOGIN TOKEN (FROM FASTAPI REDIRECT)
# -------------------------
query_params = st.query_params

if "token" in query_params and st.session_state.user is None:
    try:
        data = jwt.decode(query_params["token"], "SECRET_KEY", algorithms=["HS256"])
        st.session_state.user = data["email"]
    except:
        st.error("Invalid login token")


# -------------------------
# MODE SELECTION
# -------------------------
mode = st.radio(
    "Choose Mode",
    ["Continue as Guest", "Login for Personalized Advice"]
)


# -------------------------
# LOGIN SECTION
# -------------------------
if mode == "Login for Personalized Advice":

    if st.session_state.user is None:
        st.warning("You are not logged in")

        st.link_button(
            "Login with Google",
            "http://127.0.0.1:8000/login"
        )

    else:
        st.success(f"Logged in as {st.session_state.user}")


# -------------------------
# CHAT INTERFACE
# -------------------------
st.divider()

# Show previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# User input
user_input = st.chat_input("Ask something...")

if user_input:
    # Save user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    st.chat_message("user").write(user_input)

    # -------------------------
    # RESPONSE LOGIC
    # -------------------------
    if mode == "Continue as Guest" or st.session_state.user is None:
        # BASIC MODE
        response = get_response(user_input)

    else:
        # PERSONALIZED MODE
        response = get_response(
            f"User ({st.session_state.user}) asks: {user_input}"
        )

    # Save bot response
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
    st.chat_message("assistant").write(response)