import Markdown from 'react-markdown'
import { Link } from 'react-router-dom'

interface Section {
  title: string
  body: string
}

const TERMS: Section[] = [
  {
    title: '1. Acceptance of Terms',
    body: `By accessing and using the HealthCare AI Assistant application (hereinafter "Service"), you agree to be bound by these Terms of Service. If you do not agree to abide by the above, please do not use this service.`,
  },
  {
    title: '2. Use License',
    body: `Permission is granted to temporarily download one copy of the materials (information or software) on HealthCare AI Assistant for personal, non-commercial transitory viewing only. This is the grant of a license, not a transfer of title, and under this license you may not:

- Modifying or copying the materials
- Using the materials for any commercial purpose or for any public display
- Attempting to decompile or reverse engineer any software contained on the Service
- Removing any copyright or other proprietary notations from the materials
- Transferring the materials to another person or "mirroring" the materials on any other server
- Violating any applicable laws or regulations`,
  },
  {
    title: '3. Disclaimer',
    body: `The materials on HealthCare AI Assistant are provided on an 'as is' basis. HealthCare AI makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including, without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.`,
  },
  {
    title: '4. Limitations',
    body: `In no event shall HealthCare AI or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials on HealthCare AI, even if HealthCare AI or an authorized representative has been notified verbally or in writing of the possibility of such damage.`,
  },
  {
    title: '5. Health Disclaimer',
    body: `⚠️ **IMPORTANT NOTICE:** The HealthCare AI Assistant is designed for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment.

- The Service does not provide medical advice
- Always seek the advice of a qualified healthcare provider before making any healthcare decisions
- Never disregard professional medical advice or delay seeking it due to information obtained through this Service
- Use of this Service is at your own risk
- In case of a medical emergency, please call emergency services (911 in the US) immediately`,
  },
  {
    title: '6. Accuracy of Materials',
    body: `The materials appearing on HealthCare AI could include technical, typographical, or photographic errors. HealthCare AI does not warrant that any of the materials on its website are accurate, complete, or current. HealthCare AI may make changes to the materials contained on its website at any time without notice.`,
  },
  {
    title: '7. Modifications',
    body: `HealthCare AI may revise these terms of service for its website at any time without notice. By using this website, you are agreeing to be bound by the then current version of these terms of service.`,
  },
  {
    title: '8. Governing Law',
    body: `These terms and conditions are governed by and construed in accordance with the laws of the United States, and you irrevocably submit to the exclusive jurisdiction of the courts in that location.`,
  },
  {
    title: '9. Contact Information',
    body: `If you have any questions about these Terms of Service, please contact us through the HealthCare AI website.`,
  },
]

const PRIVACY: Section[] = [
  {
    title: '1. Introduction',
    body: `HealthCare AI ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and otherwise handle your information when you use our HealthCare AI Assistant application and related services.`,
  },
  {
    title: '2. Information We Collect',
    body: `**Information You Provide Directly:**

- Google account information (name, email, profile picture)
- Health profile data (age, gender, height, weight, health conditions, medications, allergies)
- Health metrics and wellness logs (blood pressure, weight, heart rate, blood sugar, sleep, exercise)
- Messages and conversations within the chat interface
- Calendar information for medication reminders

**Information Collected Automatically:**

- Log data (IP address, browser type, access times)
- Usage information (pages visited, features used, time spent)
- Device information (operating system, browser)`,
  },
  {
    title: '3. How We Use Your Information',
    body: `We use the information we collect for:

- **Providing Services:** Delivering personalized health advice, tracking wellness metrics, and managing medication reminders
- **Improving Services:** Analyzing usage patterns to enhance functionality and user experience
- **Communication:** Sending updates about your account or service changes
- **Security:** Detecting and preventing fraudulent activity
- **Legal Compliance:** Meeting applicable laws and regulations
- **Research:** Conducting anonymized research to improve health outcomes (with your consent)`,
  },
  {
    title: '4. Data Security',
    body: `We implement industry-standard security measures to protect your information:

- Encrypted transmission using HTTPS/TLS
- Secure authentication with Google OAuth
- Access controls limiting data access to authorized personnel
- Regular security audits and updates
- Secure password practices for backend systems

**However**, no method of transmission over the Internet or electronic storage is completely secure. We cannot guarantee absolute security of your information.`,
  },
  {
    title: '5. Third-Party Services',
    body: `Our application uses the following third-party services:

- **Google OAuth:** For authentication and calendar access
- **Google Calendar API:** For medication reminder scheduling
- **FastAPI Backend:** For processing health data and generating recommendations

These third parties have their own privacy policies. We recommend reviewing their privacy policies as we are not responsible for their practices.`,
  },
  {
    title: '6. Data Sharing',
    body: `We **DO NOT** share your personal health information with third parties except:

- As required by law or legal process
- With healthcare providers if you explicitly authorize sharing
- In aggregated, anonymized form for research purposes
- With our service providers under strict confidentiality agreements`,
  },
  {
    title: '7. Your Rights',
    body: `You have the right to:

- **Access:** Request a copy of your personal data
- **Correct:** Request correction of inaccurate information
- **Delete:** Request deletion of your account and data
- **Opt-Out:** Opt out of certain data collection practices
- **Withdraw Consent:** Withdraw consent for specific uses of your data

To exercise these rights, please contact us through the HealthCare AI website.`,
  },
  {
    title: '8. Data Retention',
    body: `We retain your information for as long as your account is active. After account deletion, we retain aggregated, anonymized data for statistical and research purposes only. Some information may be retained longer if required by law.`,
  },
  {
    title: "9. Children's Privacy",
    body: `The HealthCare AI Assistant is not intended for users under 13 years of age. We do not knowingly collect information from children. If we become aware that a child under 13 has provided us with personal information, we will delete such information immediately.`,
  },
  {
    title: '10. HIPAA Compliance',
    body: `⚠️ **Important:** The HealthCare AI Assistant is **NOT** HIPAA-compliant and should not be used to store Protected Health Information (PHI) from healthcare providers. For protected health information, please use HIPAA-compliant healthcare systems.`,
  },
  {
    title: '11. International Data Transfers',
    body: `Your information may be transferred to, stored in, and processed in countries other than your country of residence, which may have different data protection rules. By using the Service, you consent to the transfer of your information to the United States and other countries.`,
  },
  {
    title: '12. Changes to This Policy',
    body: `We may update this Privacy Policy from time to time to reflect changes in our practices or for other operational, legal, or regulatory reasons. We will notify you of material changes by posting the updated policy on our website with an updated "Last Updated" date. Your continued use of the Service after such modifications constitutes your acceptance of the updated Privacy Policy.`,
  },
  {
    title: '13. Contact Us',
    body: `If you have questions about this Privacy Policy or our privacy practices, please contact us through the HealthCare AI website.`,
  },
]

function LegalPage({ title, sections }: { title: string; sections: Section[] }) {
  return (
    <div className="page-narrow legal">
      <Link to="/">← Back to app</Link>
      <h1>{title}</h1>
      <hr />
      {sections.map((section) => (
        <section key={section.title}>
          <h2>{section.title}</h2>
          <Markdown>{section.body}</Markdown>
        </section>
      ))}
      <hr />
      <p className="caption legal-footer">© 2026 HealthCare AI. All rights reserved.</p>
    </div>
  )
}

export function Terms() {
  return <LegalPage title="📋 Terms of Service" sections={TERMS} />
}

export function Privacy() {
  return <LegalPage title="🔒 Privacy Policy" sections={PRIVACY} />
}
