"""
Privacy Policy Page - HealthCare AI Assistant
==============================================
Streamlit page displaying the Privacy Policy for the HealthCare AI application.
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add backend folder to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Page configuration
st.set_page_config(
    page_title="Privacy Policy - HealthCare AI",
    page_icon="🔒",
    layout="wide"
)

st.title("🔒 Privacy Policy")
st.caption(f"Last Updated: {datetime.now().strftime('%B %d, %Y')}")
st.divider()

st.header("1. Introduction")
st.markdown("""
HealthCare AI ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy 
explains how we collect, use, disclose, and otherwise handle your information when you use our 
HealthCare AI Assistant application and related services.
""")

st.header("2. Information We Collect")
st.markdown("""
**Information You Provide Directly:**
- Google account information (name, email, profile picture)
- Health profile data (age, gender, height, weight, health conditions, medications, allergies)
- Health metrics and wellness logs (blood pressure, weight, heart rate, blood sugar, sleep, exercise)
- Messages and conversations within the chat interface
- Calendar information for medication reminders

**Information Collected Automatically:**
- Log data (IP address, browser type, access times)
- Usage information (pages visited, features used, time spent)
- Device information (operating system, browser)
""")

st.header("3. How We Use Your Information")
st.markdown("""
We use the information we collect for:

- **Providing Services:** Delivering personalized health advice, tracking wellness metrics, 
  and managing medication reminders
- **Improving Services:** Analyzing usage patterns to enhance functionality and user experience
- **Communication:** Sending updates about your account or service changes
- **Security:** Detecting and preventing fraudulent activity
- **Legal Compliance:** Meeting applicable laws and regulations
- **Research:** Conducting anonymized research to improve health outcomes (with your consent)
""")

st.header("4. Data Security")
st.markdown("""
We implement industry-standard security measures to protect your information:

- Encrypted transmission using HTTPS/TLS
- Secure authentication with Google OAuth
- Access controls limiting data access to authorized personnel
- Regular security audits and updates
- Secure password practices for backend systems

**However**, no method of transmission over the Internet or electronic storage is completely secure. 
We cannot guarantee absolute security of your information.
""")

st.header("5. Third-Party Services")
st.markdown("""
Our application uses the following third-party services:

- **Google OAuth:** For authentication and calendar access
- **Google Calendar API:** For medication reminder scheduling
- **FastAPI Backend:** For processing health data and generating recommendations

These third parties have their own privacy policies. We recommend reviewing their privacy 
policies as we are not responsible for their practices.
""")

st.header("6. Data Sharing")
st.markdown("""
We **DO NOT** share your personal health information with third parties except:

- As required by law or legal process
- With healthcare providers if you explicitly authorize sharing
- In aggregated, anonymized form for research purposes
- With our service providers under strict confidentiality agreements
""")

st.header("7. Your Rights")
st.markdown("""
You have the right to:

- **Access:** Request a copy of your personal data
- **Correct:** Request correction of inaccurate information
- **Delete:** Request deletion of your account and data
- **Opt-Out:** Opt out of certain data collection practices
- **Withdraw Consent:** Withdraw consent for specific uses of your data

To exercise these rights, please contact us through the HealthCare AI website.
""")

st.header("8. Data Retention")
st.markdown("""
We retain your information for as long as your account is active. After account deletion, 
we retain aggregated, anonymized data for statistical and research purposes only. 
Some information may be retained longer if required by law.
""")

st.header("9. Children's Privacy")
st.markdown("""
The HealthCare AI Assistant is not intended for users under 13 years of age. 
We do not knowingly collect information from children. If we become aware that a child 
under 13 has provided us with personal information, we will delete such information immediately.
""")

st.header("10. HIPAA Compliance")
st.markdown("""
⚠️ **Important:** The HealthCare AI Assistant is **NOT** HIPAA-compliant and should not be used 
to store Protected Health Information (PHI) from healthcare providers. For protected health information, 
please use HIPAA-compliant healthcare systems.
""")

st.header("11. International Data Transfers")
st.markdown("""
Your information may be transferred to, stored in, and processed in countries other than your country 
of residence, which may have different data protection rules. By using the Service, you consent to 
the transfer of your information to the United States and other countries.
""")

st.header("12. Changes to This Policy")
st.markdown("""
We may update this Privacy Policy from time to time to reflect changes in our practices or for 
other operational, legal, or regulatory reasons. We will notify you of material changes by posting 
the updated policy on our website with an updated "Last Updated" date. Your continued use of the 
Service after such modifications constitutes your acceptance of the updated Privacy Policy.
""")

st.header("13. Contact Us")
st.markdown("""
If you have questions about this Privacy Policy or our privacy practices, please contact us through 
the HealthCare AI website.
""")

st.divider()
st.markdown("""
<div style="text-align: center; color: gray; margin-top: 2rem;">
    <p>© 2026 HealthCare AI. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
