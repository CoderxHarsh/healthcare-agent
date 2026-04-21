"""
Terms of Service Page - HealthCare AI Assistant
================================================
Streamlit page displaying the Terms of Service for the HealthCare AI application.
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add backend folder to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Page configuration
st.set_page_config(
    page_title="Terms of Service - HealthCare AI",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Terms of Service")
st.caption(f"Last Updated: {datetime.now().strftime('%B %d, %Y')}")
st.divider()

st.header("1. Acceptance of Terms")
st.markdown("""
By accessing and using the HealthCare AI Assistant application (hereinafter "Service"), 
you agree to be bound by these Terms of Service. If you do not agree to abide by the 
above, please do not use this service.
""")

st.header("2. Use License")
st.markdown("""
Permission is granted to temporarily download one copy of the materials (information or software) 
on HealthCare AI Assistant for personal, non-commercial transitory viewing only. This is the 
grant of a license, not a transfer of title, and under this license you may not:

- Modifying or copying the materials
- Using the materials for any commercial purpose or for any public display
- Attempting to decompile or reverse engineer any software contained on the Service
- Removing any copyright or other proprietary notations from the materials
- Transferring the materials to another person or "mirroring" the materials on any other server
- Violating any applicable laws or regulations
""")

st.header("3. Disclaimer")
st.markdown("""
The materials on HealthCare AI Assistant are provided on an 'as is' basis. HealthCare AI makes 
no warranties, expressed or implied, and hereby disclaims and negates all other warranties including, 
without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, 
or non-infringement of intellectual property or other violation of rights.
""")

st.header("4. Limitations")
st.markdown("""
In no event shall HealthCare AI or its suppliers be liable for any damages (including, without limitation, 
damages for loss of data or profit, or due to business interruption) arising out of the use or 
inability to use the materials on HealthCare AI, even if HealthCare AI or an authorized 
representative has been notified verbally or in writing of the possibility of such damage.
""")

st.header("5. Health Disclaimer")
st.markdown("""
⚠️ **IMPORTANT NOTICE:** The HealthCare AI Assistant is designed for informational purposes only and 
is not a substitute for professional medical advice, diagnosis, or treatment. 

- The Service does not provide medical advice
- Always seek the advice of a qualified healthcare provider before making any healthcare decisions
- Never disregard professional medical advice or delay seeking it due to information obtained 
  through this Service
- Use of this Service is at your own risk
- In case of a medical emergency, please call emergency services (911 in the US) immediately
""")

st.header("6. Accuracy of Materials")
st.markdown("""
The materials appearing on HealthCare AI could include technical, typographical, or photographic errors. 
HealthCare AI does not warrant that any of the materials on its website are accurate, complete, or current. 
HealthCare AI may make changes to the materials contained on its website at any time without notice.
""")

st.header("7. Modifications")
st.markdown("""
HealthCare AI may revise these terms of service for its website at any time without notice. 
By using this website, you are agreeing to be bound by the then current version of these terms of service.
""")

st.header("8. Governing Law")
st.markdown("""
These terms and conditions are governed by and construed in accordance with the laws of the United States, 
and you irrevocably submit to the exclusive jurisdiction of the courts in that location.
""")

st.header("9. Contact Information")
st.markdown("""
If you have any questions about these Terms of Service, please contact us through the HealthCare AI website.
""")

st.divider()
st.markdown("""
<div style="text-align: center; color: gray; margin-top: 2rem;">
    <p>© 2026 HealthCare AI. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
