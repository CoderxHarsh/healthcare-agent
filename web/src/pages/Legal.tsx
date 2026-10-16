import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Brand } from '../components/ui'
import { APP_NAME, CONTACT_EMAIL, LEGAL_LAST_UPDATED, MIN_AGE } from '../config'

interface Section {
  id: string
  title: string
  body: ReactNode
}

const mail = (
  <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>
)

/* ───────────────────────── Privacy Policy ───────────────────────── */

const PRIVACY_SUMMARY: ReactNode[] = [
  <>You sign in with Google. We keep your name, email address and profile picture to run your account.</>,
  <>
    You choose what health information to enter. We use it only to personalize answers, show your trends and manage
    your medication reminders.
  </>,
  <>
    If you add a medication reminder, {APP_NAME} creates and deletes those events in your Google Calendar. It never
    reads your other events.
  </>,
  <>Your questions and health context are processed by the AI services listed in section 5. We do not sell your data and we show no ads.</>,
  <>You can disconnect Google Calendar or delete your account and all data yourself, any time, from Account &amp; Data.</>,
]

const PRIVACY: Section[] = [
  {
    id: 'who',
    title: '1. Who we are',
    body: (
      <>
        <p>
          {APP_NAME} (“we”, “us”) is a personal health companion web application that lets adults chat with an AI
          assistant, track health measurements, manage medications and get general wellness insights. {APP_NAME} is
          operated from India. This Privacy Policy explains what information we collect, why, who receives it, and the
          choices you have.
        </p>
        <p>
          <strong>Contact for privacy questions and requests:</strong> {mail}
        </p>
      </>
    ),
  },
  {
    id: 'collect',
    title: '2. Information we collect',
    body: (
      <>
        <h3>From your Google account</h3>
        <ul>
          <li>Your name, email address, profile picture and Google account identifier, when you sign in with Google.</li>
          <li>
            If you add medication reminders: a Google authorization (refresh token) that lets {APP_NAME} create and
            delete the reminder events it makes in your Google Calendar. See section 3.
          </li>
        </ul>
        <h3>Information you give us</h3>
        <ul>
          <li>
            Health profile: age, gender, height, weight, existing conditions, current medications, allergies, fitness
            level and health goals.
          </li>
          <li>Health measurements you log or mention in chat: blood pressure, weight, heart rate, blood sugar, sleep, exercise, temperature, and any notes.</li>
          <li>Medications you add, their schedule, and whether you marked each dose taken or skipped.</li>
          <li>Documents you upload (PDF, TXT or Markdown). We store the extracted text, split into passages, and a numerical representation of each passage so the assistant can search it for you.</li>
          <li>Messages you type to the assistant. Conversations are not saved in our database; see section 5.</li>
        </ul>
        <h3>Collected automatically</h3>
        <ul>
          <li>Basic technical data in server logs, such as request time, error messages and IP address, used to run and secure the service.</li>
          <li>
            Your browser’s local storage holds a sign-in token and your account number so you stay signed in. We do
            not use advertising or analytics cookies. Pages load the Inter font from Google Fonts, which means your
            browser contacts Google to fetch it.
          </li>
        </ul>
      </>
    ),
  },
  {
    id: 'google',
    title: '3. Google user data',
    body: (
      <>
        <p>{APP_NAME} asks for these Google permissions:</p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Permission</th>
                <th>What we use it for</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Name, email address, profile picture (OpenID, email, profile)</td>
                <td>To sign you in, create your account and show who is signed in.</td>
              </tr>
              <tr>
                <td>
                  Google Calendar events (<code>calendar.events</code>)
                </td>
                <td>
                  Only to create a recurring reminder when you add a medication, and to delete that reminder when you
                  remove the medication, disconnect Calendar or delete your account.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <ul>
          <li>We do not read, list, copy or analyze your other calendar events, and we do not access other Google services.</li>
          <li>Calendar access is optional. You can use {APP_NAME} without adding reminders.</li>
          <li>We never sell Google user data, use it for advertising, or share it with data brokers.</li>
          <li>
            We do not send your Google email address, profile picture or any Calendar data to the AI services in section 5.
            Your name is included in AI requests so answers can address you personally.
          </li>
          <li>
            Disconnect any time from <Link to="/account">Account &amp; Data</Link>, or remove access from your Google
            Account at{' '}
            <a href="https://myaccount.google.com/permissions" target="_blank" rel="noreferrer">
              myaccount.google.com/permissions
            </a>
            .
          </li>
        </ul>
        <p className="legal-summary" style={{ margin: '16px 0' }}>
          {APP_NAME}’s use and transfer to any other app of information received from Google APIs will adhere to the{' '}
          <a href="https://developers.google.com/terms/api-services-user-data-policy" target="_blank" rel="noreferrer">
            Google API Services User Data Policy
          </a>
          , including the Limited Use requirements.
        </p>
      </>
    ),
  },
  {
    id: 'use',
    title: '4. How we use your information',
    body: (
      <>
        <ul>
          <li>To provide the service: sign-in, your profile, charts and dashboard, medication tracking and reminders, PDF reports.</li>
          <li>To personalize AI answers using your profile, recent readings and uploaded documents.</li>
          <li>To keep the service secure, prevent abuse and fix errors.</li>
          <li>To respond to your requests and to meet legal obligations.</li>
        </ul>
        <p>
          We do not sell your information, we do not show advertising, and we do not use your data to train our own
          models. We do not make decisions about you by automated means that have legal or similarly significant
          effects.
        </p>
      </>
    ),
  },
  {
    id: 'processors',
    title: '5. Service providers that process your data',
    body: (
      <>
        <p>
          We use the following providers to run {APP_NAME}. Each receives only what is needed for its task and handles
          it under its own terms and privacy policy.
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Provider</th>
                <th>What it receives</th>
                <th>Why</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Google (Sign-In, Calendar)</td>
                <td>Sign-in request; calendar reminders you ask for</td>
                <td>Authentication and reminders</td>
              </tr>
              <tr>
                <td>Groq (AI language model)</td>
                <td>
                  Your message, recent conversation, your name, and the parts of your health profile and recent readings
                  relevant to chat
                </td>
                <td>To generate chat replies</td>
              </tr>
              <tr>
                <td>Anthropic (AI language model)</td>
                <td>Your name and summarized vital readings and trends</td>
                <td>To write the short dashboard analysis</td>
              </tr>
              <tr>
                <td>Google Gemini API (embeddings)</td>
                <td>Text passages of documents you upload and the text of your questions</td>
                <td>To search your documents</td>
              </tr>
              <tr>
                <td>MedlinePlus (U.S. National Library of Medicine)</td>
                <td>Text of general medical questions such as “what is…” or “symptoms of…”</td>
                <td>To fetch public health information</td>
              </tr>
              <tr>
                <td>Neon (managed PostgreSQL database)</td>
                <td>All data we store: account, health data, documents</td>
                <td>Storage</td>
              </tr>
              <tr>
                <td>Render and our web hosting provider</td>
                <td>Technical request data; traffic to the app</td>
                <td>Hosting the backend and the website</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p>
          <strong>Chat messages</strong> are sent to the AI provider to produce a reply and are kept in your browser
          only while the page is open. We do not store conversations in our database. Health measurements you mention
          in chat (for example “my BP is 120/80”) are detected and saved to your health log so they appear in your
          charts.
        </p>
        <p>
          Please avoid typing information about other people or details you do not wish to be processed by these
          providers.
        </p>
      </>
    ),
  },
  {
    id: 'sharing',
    title: '6. When we share information',
    body: (
      <>
        <p>We share personal information only:</p>
        <ul>
          <li>with the providers in section 5, to operate the service;</li>
          <li>when you ask us to, for example when you download your own PDF report;</li>
          <li>when the law requires it, or to protect rights, safety and security.</li>
        </ul>
        <p>We do not sell or rent personal information and we do not share it for advertising.</p>
      </>
    ),
  },
  {
    id: 'security',
    title: '7. How we protect your information',
    body: (
      <ul>
        <li>All traffic between your browser, our servers and our providers uses HTTPS (TLS).</li>
        <li>Every request for personal data must carry a signed session token, and you can reach only your own records.</li>
        <li>Your Google Calendar authorization token is encrypted before it is stored.</li>
        <li>Administrative and diagnostic functions are disabled for the public and need a secret key.</li>
        <li>Our database provider stores data in a managed, access-controlled environment.</li>
      </ul>
    ),
  },
  {
    id: 'retention',
    title: '8. How long we keep your information',
    body: (
      <>
        <p>
          We keep your information while your account is active. When you delete your account from{' '}
          <Link to="/account">Account &amp; Data</Link>, we immediately delete your profile, health logs, medications,
          dose history and uploaded-document data from our live database, delete the reminder events we created in your
          Google Calendar, and revoke our Google access. Backups held by our database provider may retain deleted data
          for a short period until they are overwritten. Server logs are kept only as long as needed for security and
          troubleshooting.
        </p>
      </>
    ),
  },
  {
    id: 'rights',
    title: '9. Your choices and rights',
    body: (
      <>
        <ul>
          <li>
            <strong>Access:</strong> download a PDF of your health information from Account &amp; Data, or ask us for a copy.
          </li>
          <li>
            <strong>Correction:</strong> edit your profile, goals, logs and medications in the app, or ask us to correct them.
          </li>
          <li>
            <strong>Deletion:</strong> delete your account and data yourself in Account &amp; Data, or ask us.
          </li>
          <li>
            <strong>Withdraw consent:</strong> disconnect Google Calendar, or stop using the service and delete your account.
          </li>
          <li>
            <strong>Complaints:</strong> write to {mail}. We will acknowledge your request promptly and respond within 30 days.
            You may also have the right to complain to a data protection authority.
          </li>
        </ul>
        <p>
          If you are in India, these choices reflect your rights under the Digital Personal Data Protection Act, 2023.
          If you are in the European Economic Area or United Kingdom, you may also have rights under the GDPR, including
          portability and objection.
        </p>
      </>
    ),
  },
  {
    id: 'sensitive',
    title: '10. Health information',
    body: (
      <p>
        Health information is sensitive. {APP_NAME} is a wellness and information tool. It is not a medical device, it
        is not provided by a healthcare provider, and it is not a service covered by HIPAA. Do not use it to store
        records from your doctor that you are legally required to keep in a regulated system. You provide health
        information voluntarily and can remove it at any time.
      </p>
    ),
  },
  {
    id: 'age',
    title: '11. Age requirement',
    body: (
      <p>
        {APP_NAME} is for adults aged {MIN_AGE} or older. We do not knowingly collect information from anyone younger.
        If you believe a minor has provided information, contact {mail} and we will delete it.
      </p>
    ),
  },
  {
    id: 'transfers',
    title: '12. International transfers',
    body: (
      <p>
        We operate from India. Our providers may process data in other countries, including the United States. By using
        {' '}{APP_NAME}, you understand your information may be transferred to and processed in those countries, with the
        protections described in this policy.
      </p>
    ),
  },
  {
    id: 'changes',
    title: '13. Changes to this policy',
    body: (
      <p>
        We may update this policy as the service changes. We will change the “Last updated” date above and, for
        material changes, show a notice in the app. If we ever want to use Google user data in a new way, we will ask
        for your permission first.
      </p>
    ),
  },
  {
    id: 'contact',
    title: '14. Contact us',
    body: (
      <p>
        Questions, requests or complaints about privacy: {mail}. See also our <Link to="/terms">Terms of Service</Link>.
      </p>
    ),
  },
]

/* ───────────────────────── Terms of Service ───────────────────────── */

const TERMS_SUMMARY: ReactNode[] = [
  <>{APP_NAME} gives general wellness information. It is not medical advice and does not replace a doctor.</>,
  <>In an emergency, call your local emergency number (112 in India, 911 in the US) immediately.</>,
  <>You must be {MIN_AGE} or older and provide accurate information.</>,
  <>AI answers can be wrong. Check anything important with a qualified professional.</>,
]

const TERMS: Section[] = [
  {
    id: 'accept',
    title: '1. Agreement',
    body: (
      <p>
        These Terms of Service govern your use of {APP_NAME} (the “Service”). By signing in or using the Service you
        agree to these Terms and to our <Link to="/privacy">Privacy Policy</Link>. If you do not agree, do not use the
        Service.
      </p>
    ),
  },
  {
    id: 'medical',
    title: '2. Not medical advice',
    body: (
      <>
        <p>
          <strong>
            {APP_NAME} provides general information for wellness and education only. It does not provide medical advice,
            diagnosis or treatment, and it does not create a doctor–patient relationship.
          </strong>
        </p>
        <ul>
          <li>Always seek the advice of a qualified healthcare professional about any medical condition or before changing medication, diet or exercise.</li>
          <li>Never ignore professional advice or delay seeking it because of something you read in {APP_NAME}.</li>
          <li>Reference ranges and status labels (such as “in range” or “outside range”) are general guides, not a diagnosis.</li>
          <li>
            <strong>In an emergency, contact your local emergency services immediately</strong> (112 or 108 in India,
            911 in the United States). Do not rely on {APP_NAME} in an emergency.
          </li>
        </ul>
      </>
    ),
  },
  {
    id: 'ai',
    title: '3. AI-generated content',
    body: (
      <p>
        Replies, summaries and analyses are generated by artificial intelligence and by automated rules. They may be
        incomplete, out of date or wrong. You are responsible for how you use them. Medication reminders and dose
        tracking are conveniences and may fail; do not depend on them for critical care.
      </p>
    ),
  },
  {
    id: 'eligibility',
    title: '4. Eligibility and your account',
    body: (
      <ul>
        <li>You must be at least {MIN_AGE} years old.</li>
        <li>You sign in with your Google account and are responsible for activity under it.</li>
        <li>Give accurate information and keep it up to date. Do not enter information about another person without their permission.</li>
      </ul>
    ),
  },
  {
    id: 'use',
    title: '5. Acceptable use',
    body: (
      <>
        <p>You agree not to:</p>
        <ul>
          <li>break the law or infringe anyone’s rights;</li>
          <li>attempt to access another person’s data, probe, overload or disrupt the Service, or bypass its security;</li>
          <li>upload malware or content you do not have the right to share;</li>
          <li>copy, resell or reverse engineer the Service, except as the law allows;</li>
          <li>use the Service to provide medical services to others, or to make clinical decisions.</li>
        </ul>
      </>
    ),
  },
  {
    id: 'content',
    title: '6. Your content',
    body: (
      <p>
        You keep ownership of the information and documents you provide. You give us permission to store and process
        them only to provide the Service to you, as described in the Privacy Policy, including by sending them to the
        service providers listed there. You can delete your content or your whole account at any time in{' '}
        <Link to="/account">Account &amp; Data</Link>.
      </p>
    ),
  },
  {
    id: 'google',
    title: '7. Google Calendar',
    body: (
      <p>
        If you choose to add medication reminders, you authorize {APP_NAME} to create and delete the reminder events it
        makes in your Google Calendar. You can revoke this at any time in Account &amp; Data or in your Google Account
        settings. Our use of information received from Google APIs follows the Google API Services User Data Policy,
        including the Limited Use requirements.
      </p>
    ),
  },
  {
    id: 'availability',
    title: '8. Availability and changes',
    body: (
      <p>
        We work to keep the Service available but do not guarantee uninterrupted or error-free operation. We may change,
        suspend or discontinue features, and we may update these Terms; the “Last updated” date shows the current version.
        Continued use after a change means you accept the updated Terms.
      </p>
    ),
  },
  {
    id: 'disclaimer',
    title: '9. Disclaimer of warranties',
    body: (
      <p>
        The Service is provided “as is” and “as available”, without warranties of any kind, express or implied,
        including accuracy, fitness for a particular purpose and non-infringement, to the fullest extent permitted by law.
      </p>
    ),
  },
  {
    id: 'liability',
    title: '10. Limitation of liability',
    body: (
      <p>
        To the fullest extent permitted by law, we are not liable for indirect, incidental, special or consequential
        damages, or for loss of data, health outcomes or profits arising from your use of or inability to use the
        Service. Nothing in these Terms limits liability that cannot be limited by law.
      </p>
    ),
  },
  {
    id: 'termination',
    title: '11. Ending your use',
    body: (
      <p>
        You can stop using the Service and delete your account at any time. We may suspend or end access if you breach
        these Terms or if needed to protect the Service or other people. Sections that by their nature should survive
        (such as disclaimers and limits of liability) will continue after termination.
      </p>
    ),
  },
  {
    id: 'law',
    title: '12. Governing law',
    body: (
      <p>
        These Terms are governed by the laws of India. Subject to any rights you have under mandatory consumer laws,
        the courts of India have jurisdiction over any dispute.
      </p>
    ),
  },
  {
    id: 'contact',
    title: '13. Contact',
    body: (
      <p>
        Questions about these Terms: {mail}. Privacy requests: see the <Link to="/privacy">Privacy Policy</Link>.
      </p>
    ),
  },
]

/* ───────────────────────── Page ───────────────────────── */

function LegalPage({
  title,
  intro,
  summaryTitle,
  summary,
  sections,
}: {
  title: string
  intro: string
  summaryTitle: string
  summary: ReactNode[]
  sections: Section[]
}) {
  return (
    <div className="legal-wrap">
      <header className="legal-top">
        <Brand />
        <Link to="/" className="btn btn-secondary btn-small">
          <ArrowLeft className="icon" size={14} aria-hidden="true" />
          Back to {APP_NAME}
        </Link>
      </header>

      <div className="legal-layout">
        <nav className="legal-toc" aria-label={`${title} contents`}>
          <strong style={{ color: 'var(--text)' }}>On this page</strong>
          <ol>
            {sections.map((s) => (
              <li key={s.id}>
                <a href={`#${s.id}`}>{s.title}</a>
              </li>
            ))}
          </ol>
        </nav>

        <article className="legal-body">
          <h1>{title}</h1>
          <p className="caption">Last updated: {LEGAL_LAST_UPDATED}</p>
          <p>{intro}</p>

          <aside className="legal-summary" aria-label={summaryTitle}>
            <h2>{summaryTitle}</h2>
            <ul>
              {summary.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </aside>

          {sections.map((section) => (
            <section key={section.id} id={section.id} aria-labelledby={`${section.id}-h`}>
              <h2 id={`${section.id}-h`}>{section.title}</h2>
              {section.body}
            </section>
          ))}

          <p className="caption legal-footer">
            © 2026 {APP_NAME}. <Link to="/terms">Terms of Service</Link> · <Link to="/privacy">Privacy Policy</Link>
          </p>
        </article>
      </div>
    </div>
  )
}

export function Terms() {
  return (
    <LegalPage
      title="Terms of Service"
      intro={`Please read these terms carefully before using ${APP_NAME}.`}
      summaryTitle="In short"
      summary={TERMS_SUMMARY}
      sections={TERMS}
    />
  )
}

export function Privacy() {
  return (
    <LegalPage
      title="Privacy Policy"
      intro={`Your health information is personal. This policy explains exactly what ${APP_NAME} collects, why, and the control you have.`}
      summaryTitle="Summary"
      summary={PRIVACY_SUMMARY}
      sections={PRIVACY}
    />
  )
}
