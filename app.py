import streamlit as st
from chatbot import get_response

st.title("🏥 Your Health Chatbot")

# -------------------------
# SESSION SETUP
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user" not in st.session_state:
    st.session_state.user = None

if "onboarded" not in st.session_state:
    st.session_state.onboarded = None


# -------------------------
# CHECK LOGIN (FROM FASTAPI REDIRECT)
# -------------------------
params = st.query_params

# FastAPI sends: ?user=email@gmail.com&onboarded=true/false
if "user" in params and st.session_state.user is None:
    st.session_state.user = params["user"]
    st.session_state.onboarded = params.get("onboarded", "false")


# -------------------------
# ROUTING BASED ON LOGIN STATE
# -------------------------
if st.session_state.user:
    # ✅ USER IS LOGGED IN — skip radio buttons entirely
    st.success(f"Logged in as {st.session_state.user}")

    if st.session_state.onboarded == "false":
        st.info("Please complete your health profile first!")
        st.link_button("Complete Onboarding", "http://127.0.0.1:8000/onboarding")
        st.stop()  # ← don't show chat until onboarded

else:
    # ❌ USER IS NOT LOGGED IN — show mode selection
    mode = st.radio(
        "Choose Mode",
        ["Continue as Guest", "Login for Personalized Advice"]
    )

    if mode == "Login for Personalized Advice":
        st.warning("Please log in with your Google account to get personalized health advice based on your profile.")
        st.link_button("Login with Google", "http://127.0.0.1:8000/login")
        st.stop()  # ← don't show chat in this mode until logged in


# -------------------------
# CHAT INTERFACE
# -------------------------
st.divider()

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Personalized if logged in, basic if guest
    if st.session_state.user:
        response = get_response(f"User ({st.session_state.user}) asks: {user_input}")
    else:
        response = get_response(user_input)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)