# HealthAgent — Design Specification

Design brief for generating the HealthAgent UI in Google Stitch. Every screen, field, and state below is taken from the existing React app in `web/src`. Nothing here adds product features. Items that are visual changes only (such as replacing emoji with icons) are marked **[visual change]**.

---

## 1. Product overview

**HealthAgent** ("HealthCare AI Assistant", subtitle "AI Health Monitor") is a personal health companion. A signed-in user can:

| Capability | Where it lives |
|---|---|
| Chat with an AI health assistant that knows their profile, recent vitals, and uploaded documents | `/chat` (guests can chat too, from the landing page) |
| Upload a PDF/TXT health document to personalize AI answers | `/chat` upload card |
| See latest vitals and an AI-written analysis of their data | `/dashboard` |
| Set health goals and view progress trends (weight, sleep, blood pressure) | `/goals` |
| Log metrics manually, browse history, view a summary, bulk-import CSV/JSON/XML | `/wellness` (4 tabs) |
| Manage medications, log doses taken/skipped, see an adherence report, optional Google Calendar reminders | `/medications` (3 tabs) |
| Complete a one-time health profile | `/onboarding` |
| Download a PDF health report | Top-bar button |
| Read the Terms of Service and Privacy Policy | `/terms`, `/privacy` |

Metrics are also extracted automatically from chat messages (for example "I weigh 70kg today") and saved to the log.

**Target users:** adults managing their own wellbeing, such as people tracking blood pressure, weight, sleep, heart rate, blood sugar, exercise, or daily medications. Many are managing a chronic condition (diabetes, hypertension, heart disease, asthma, thyroid, arthritis, depression/anxiety are the onboarding options). They range from non-technical to comfortable with apps. They often use the app on a phone and sometimes while unwell, so legibility and calm matter more than density.

**Not in the product (do not design):** appointments, doctor or clinician accounts, telehealth or video, messaging with humans, insurance, lab-result import, wearable sync, notifications center, social features, payments, multi-user or family profiles.

**Auth model:** Google sign-in only. Signed-out visitors see the landing page with a guest chat.

---

## 2. Visual direction

**Keywords:** calm, clinical-but-warm, trustworthy, precise, quietly intelligent.

- **Light theme only for this design pass.** Warm, soft, and calming rather than cold and clinical: generous whitespace, rounded shapes, gentle teal and sage tones. The dark theme in section 3.2 is a future option and must not be generated now.
- **Not a generic admin dashboard.** Avoid dense KPI grids, heavy gradients, neon accents, and glassmorphism. Lead with the person ("Good morning, Priya"), not with system data. Use whitespace and large readable numbers.
- **AI is present but never mystical.** No robots, sparkles, or brains. AI-written content sits in a distinct "AI insight" card with a plain label and the same assistant avatar everywhere (a small teal-blue rounded mark with a cross or pulse glyph).
- **Status is never color-only.** Every green/amber/red state also has an icon and a text label.
- **Tone of voice:** plain, warm, short sentences. Reassure without diagnosing.
- **Iconography:** one outline icon family (Lucide, 1.75px stroke, 20px default). **[visual change]** Replace the current emoji (🏥 💊 📊 🎯 …) with icons everywhere. Emoji render differently per platform and read as unserious.
- **Imagery:** none required. No stock photos of doctors. At most, one subtle abstract pulse line motif on the landing hero.

### Brand mark
A rounded-square mark in `primary-600` with a white medical cross whose horizontal arm is a small pulse line, next to the wordmark **HealthAgent** (Inter 600) and the caption "AI Health Monitor".

---

## 3. Color system

The app's current bright blue (`#20A4F3`) is replaced by a softer, deeper teal that is calmer and also passes text contrast on white.

### 3.1 Light theme (the primary and only launch theme)

**Palette intent: comforting and calming.** Soft teal (water, calm) as the main color, sage green (nature, recovery) as the secondary, and a warm off-white background instead of cold clinical white. Alert colors are muted so a reading outside range informs rather than frightens. No saturated reds or neon blues on large areas.

| Token | HEX | Use |
|---|---|---|
| `primary-600` | `#2F7F86` | Primary buttons, links, active nav, focus ring base (4.7:1 on white) |
| `primary-700` | `#25666C` | Primary hover/pressed |
| `primary-500` | `#5AA9AE` | Chart lines, decorative accents, progress fills (not for small text) |
| `primary-100` | `#CFE6E7` | Info notice border, chip backgrounds |
| `primary-50` | `#EAF4F4` | Active nav background, info notice background, selected rows |
| `secondary-600` | `#4F7352` | Sage accent: AI insight card accent bar, assistant avatar (5.4:1) |
| `secondary-50` | `#EEF4EE` | AI insight card background |
| `bg` | `#FAF8F5` | App background (warm off-white) |
| `surface` | `#FFFFFF` | Cards, sidebar, inputs |
| `surface-sunken` | `#F3F0EB` | Table header, secondary button hover |
| `border` | `#E6E1DA` | Card borders, dividers |
| `border-strong` | `#8F887E` | Input borders (3.5:1 on white), hover border |
| `text` | `#1F2D33` | Headings, values (about 14:1) |
| `text-soft` | `#3F4F57` | Body text (about 8.5:1) |
| `text-muted` | `#5E6B72` | Captions, labels, helper text (5.5:1) |
| `success-700` | `#2E7D4F` | Success text/icon (5.0:1) |
| `success-50` | `#E9F5EE` | Success background |
| `success-500` | `#5DB287` | Chart/dot fill only |
| `warning-700` | `#8A5A00` | Warning text/icon (about 6:1) |
| `warning-50` | `#FFF5E0` | Warning background |
| `warning-500` | `#E5A93D` | Chart/dot fill only |
| `error-700` | `#A63A32` | Error text/icon (6.4:1) |
| `error-50` | `#FBEDEB` | Error background |
| `error-500` | `#D9776B` | Chart/dot fill only |

### 3.2 Dark theme (variant, carries over today's palette)

| Token | HEX |
|---|---|
| `bg` | `#0E1117` |
| `sidebar` / `surface-sunken` | `#14171E` |
| `surface` | `#171A21` |
| `input` | `#0F1116` |
| `border` | `#FFFFFF` at 8% (`rgba(255,255,255,0.08)`) |
| `text` | `#F8FAFC` |
| `text-soft` | `#CBD5E1` |
| `text-muted` | `#94A3B8` |
| `primary` (buttons, links) | `#20A4F3` with white-on-blue limited to 16px+ semibold labels; use `#2F7F86` fill if body-size label contrast is needed |
| `success` / `warning` / `error` text | `#34D399` / `#FBBF24` / `#F87171` |

### 3.3 Reference ranges (status logic already in the app)
Status dots on vitals follow these ranges. Show them as helper text where a value is judged:
- Heart rate **60–100 bpm**
- Sleep **7–9 hours**
- Blood pressure **systolic 90–120, diastolic 60–80 mmHg**
- Weight and other metrics have no range, so show a neutral gray status.

Status vocabulary: **In range** (green, check-circle icon), **Outside range** (amber, alert-triangle icon), **No reference** (gray, minus-circle icon). Never label a value "dangerous", "abnormal", or "critical". The app does not diagnose.

### 3.4 Chart colors
Series 1 `#5AA9AE`, series 2 `#8AA88C`, systolic `#D9776B`, diastolic `#6B8FC4`. Gridlines `#E6E1DA`. Axis text `#5E6B72`, 12px.

---

## 4. Typography

**Family:** **Inter** (system-ui fallback). **[visual change]** The app currently uses Outfit, which is geometric and displays well but has lower legibility for dense numbers. Inter has tabular numerals, which matter for vitals. Use `font-variant-numeric: tabular-nums` on all values and table numbers.

| Role | Size / line-height | Weight | Color |
|---|---|---|---|
| Display (landing hero) | 40 / 48 (28/36 mobile) | 700 | `text` |
| H1 (page title) | 28 / 36 (24/32 mobile) | 700 | `text` |
| H2 (section) | 20 / 28 | 600 | `text` |
| H3 (card title) | 16 / 24 | 600 | `text` |
| Body | 16 / 24 | 400 | `text-soft` |
| Body small (table, helper) | 14 / 20 | 400 | `text-soft` |
| Label (form label) | 14 / 20 | 500 | `text` |
| Overline (metric card title) | 12 / 16, uppercase, +0.08em tracking | 600 | `text-muted` |
| Caption | 13 / 18 | 400 | `text-muted` |
| Metric value (large) | 36 / 40 | 700 | `text` |
| Metric unit | 14 / 20 | 500 | `text-muted` |
| Button label | 15 / 20 | 600 | per variant |

Rules: nothing below 12px, and the only 12px text is the overline. Body text is never lighter than `text-muted`. Line length in chat bubbles and the AI analysis is capped at about 70 characters. Do not set body text in all caps.

---

## 5. Layout and navigation

### 5.1 App shell (signed-in)
- **Desktop (≥1024px):** left sidebar 264px fixed + main content. Main content max width **1120px**, centered in the remaining space, with 32px horizontal padding and 32px top padding.
- **Sidebar (surface, 1px right border):** top: brand mark; middle: nav list; bottom: signed-in user chip (avatar initial, name, "Signed in") with Logout, then "Terms of Service" and "Privacy Policy" text links.
- **Nav items (5, in this order):** Chat, Dashboard, Goals, Wellness, Medications. Icons: message-circle, layout-dashboard, target, activity, pill. **[visual change]** Today every nav item is a full-width button; use quieter list items with an active state instead.
- **Top bar (within main):** page title (H1) with a one-line description on the left; **PDF Report** secondary button with a download icon on the right. This is today's behavior, where the report opens in a new tab.
- **Tablet (640–1023px):** sidebar collapses to a 72px icon rail with tooltips; main padding 24px.
- **Mobile (<640px):** sidebar becomes a **bottom tab bar** with the 5 nav items (icon + 11px label, 56px high, safe-area aware). Brand and user/logout move into a header with an avatar menu. Terms and Privacy go in that menu. PDF Report becomes an icon button in the header. Main padding 16px.

### 5.2 Guest shell (landing)
Same sidebar structure with a different body: info notice ("Log in to access your personal dashboard, track vitals, and get tailored AI insights"), a **Continue with Google** button, then the legal links. On mobile the sidebar content moves into a top header with a "Log in" button.

### 5.3 Page types
- **Wide pages** (Dashboard, Goals, Wellness, Medications, Chat): inside the shell, max 1120px.
- **Narrow page** (Onboarding, Terms, Privacy): single centered column, max **720px**, no sidebar.
- **Full-page messages** (loading profile, load error): vertically centered, with Retry and Log out buttons on error.

### 5.4 Spacing and grid
- 4px base unit. Scale: 4, 8, 12, 16, 24, 32, 48, 64.
- 12-column grid at ≥1024px, 24px gutters; 8 columns on tablet; 4 columns on mobile with 16px gutters.
- Card padding 24px (20px mobile). Gap between cards 16px. Section gap 32px.
- Radii: inputs/buttons 10px, cards 16px, chips/badges 999px, chat bubbles 18px (4px on the tail corner).
- Elevation: cards use border only (no shadow) by default. Popovers, toasts, and dialogs use `0 8px 24px rgba(15,31,46,0.12)`.

---

## 6. Screen specifications

Design all screens at desktop (1440×900) first, then mobile (390×844). Use the same data in each (see 6.10).

### 6.1 Landing (guest, `/`)
1. Guest shell (5.2).
2. **Hero:** Display "Your AI health companion." with the subtitle "Chat, track vitals, manage meds and get personalized insights." Five feature chips, each with its own icon and calm tint: AI Chat, Vitals, Medications, RAG Docs ("Your documents"), PDF Reports.
3. Divider, then **"Try it now — chat as a guest"** (H2) with the caption "Log in with Google to unlock personalized insights, vitals tracking, and your private health history."
4. **Chat panel** (see 6.2 chat component) in a bordered card, min height 420px. The first assistant message is a greeting. The composer is placed at the bottom of the card.
5. Footer row: Terms · Privacy.

### 6.2 Chat (`/chat`)
- Top: **Upload card** (compact, dashed border): file icon, "Upload a health document (PDF or TXT) to personalize AI answers", a **Choose file** button. States in section 8.
- **Message list** fills the remaining height and scrolls. Max reading width 720px, left-aligned.
  - **Assistant bubble:** surface, 1px border, assistant avatar at left. Supports Markdown (paragraphs, bullet and numbered lists, bold). The backend prepends a small italic **topic badge** (for example the tool name) to some replies; render it as a small tag above the text.
  - **User bubble:** right-aligned, `primary-600` fill, white text.
  - **Pending:** assistant bubble with the typing indicator and "Thinking…" label.
- **Composer (sticky bottom):** single-line text input, placeholder "Ask me about your health…", circular **Send** icon button, disabled when empty or pending.
- Beneath the composer, one caption line: "HealthAgent provides general information, not medical advice." **[visual change]** A static trust line. It adds no function.

### 6.3 Onboarding (`/onboarding`, narrow page, shown once)
Title "Complete your health profile", subtitle "Help us know you better." A **3-step visual grouping** on a single scrolling form (not a wizard, because the app submits it as one form):
1. **About you:** Age (number), Gender (select: Male, Female, Other, Prefer not to say), Height cm, Weight kg. Two-column grid on desktop.
2. **Health background:** Existing conditions (checkbox group: Diabetes, Hypertension (High Blood Pressure), Heart Disease, Asthma, Thyroid, Arthritis, Depression/Anxiety, None, Other), Current medications (textarea), Allergies (textarea).
3. **Lifestyle and goals:** Fitness level (select: Sedentary, Light, Moderate, Active, Very Active), Health goals (checkbox group: Weight Loss, Weight Gain, Build Muscle, Improve Endurance, Reduce Stress, Better Sleep, General Wellness, Manage Disease).
- Required: Age, Gender, Height, Weight, Fitness level. Mark required fields with "(required)" text and optional ones with "(optional)".
- A single full-width primary **Save and continue** button. A privacy reassurance line above it: "Your information is private and used only to personalize your experience."
- Error: error notice above the button ("Please fill in all required fields…").
- Checkbox groups render as selectable **chips** (checkbox semantics, 44px high) in a wrapping grid. **[visual change]**

### 6.4 Dashboard (`/dashboard`)
Title "Dashboard", description "Overview of your vitals."

Layout (desktop):
- **Row 1, four vital cards** (equal width): Heart Rate (bpm), Blood Pressure, Sleep (h), Weight (kg). Each card shows: overline title, the large latest value with unit, the change line ("↑ +2 bpm since last reading", "No change since last reading", "Only one reading so far"), and a status chip (In range / Outside range / No reference). Empty: "--" value with the caption "No reading yet".
- **Row 2, two cards (50/50):**
  - **Vitals Summary** table-like card: 4 rows (Heart Rate, Blood Pressure, Sleep, Weight) with a status icon + label, latest value, and unit.
  - **AI Analysis** card (`secondary-50`, 3px `secondary-600` left bar, assistant avatar). Body: the 3–4 line analysis text. Footer: result badge (**Generated** in green or **Check needed** in amber/red when the analysis failed), a neutral **ML powered** badge, and a **Refresh** secondary small button.
- Below Row 2: a caption "Reference ranges: Heart rate 60–100 bpm · Sleep 7–9 h · Blood pressure 90–120 / 60–80 mmHg."
- The dashboard loads the last 90 days of logs.

Tablet: the four cards become 2×2. Mobile: the four cards become a horizontal 2×2 compact grid (value 28px) and the Row 2 cards stack, with the AI Analysis card first.

States: loading (skeleton cards and "Analyzing your health data…" in the AI card), error (error notice at top: "Could not load health data"), empty (all "--", with a card prompting "Log your first reading in Wellness or tell the chat").

### 6.5 Goals (`/goals`)
Title "Health Goals", description "Track and update your personal health objectives."
- **Two-column area (2fr / 1fr):**
  - **Active Goals** card: list of goals, each with a goal icon (scale, run, sleep, nutrition, stress, water, or target as the default, chosen by keyword) and the goal text. Empty: centered target icon and "No health goals set yet. Add your first goal →".
  - **Edit Goals** card (collapsible, open when there are no goals): Goals (textarea, placeholder "e.g. Lose 5kg, Run 5km, Sleep 8 hours daily"), Weight (kg) number input, Fitness level select (sedentary, light, moderate, active, very active), **Save goals** primary button.
- **Progress Trends** (H2), each trend in its own card:
  - **Weight Trend** — line chart (kg, daily mean).
  - **Sleep Consistency** — bar chart (hours, daily mean), with the 7–9 h band shaded lightly. **[visual change]**
  - **Blood Pressure Trend (mmHg)** — two-line chart, systolic (red) and diastolic (blue), with a legend.
  - Weight and Sleep sit side by side; Blood Pressure is full width.
- Chart empty states (verbatim intent): "No weight data logged recently. Tell the chatbot 'I weigh 70kg today' to see your chart!" and the equivalents for sleep ("I slept 7 hours") and blood pressure ("My BP is 120/80"). Show these in a dashed empty area with an icon and a **Go to Chat** text link.
- The Goals page is code-split and shows a skeleton while loading.

### 6.6 Wellness (`/wellness`)
Title "Your Wellness Tracker." A **tab bar** with 4 tabs: **View Logs**, **Add Metric**, **Summary**, **Bulk Import**.

- **View Logs:** filter row: Metric select (All Metrics, Blood Pressure, Weight, Heart Rate, Blood Sugar, Sleep, Exercise) and a "Show last N days" slider (1–90, default 30) with the current value shown. A **table**: Date (formatted `YYYY-MM-DD HH:mm`), Metric (title case), Value (with unit), Notes. Empty: "No metrics logged yet. Add one in the Add Metric tab" with a button that switches tabs.
- **Add Metric:** Metric type select (Blood Pressure mmHg, Weight kg, Heart Rate bpm, Blood Sugar mg/dL, Sleep hours, Exercise minutes, Temperature °C), Value text input with the dynamic label "Value in {unit} (e.g., 120/80, 75.5, 8)", Notes textarea (optional), full-width **Save metric** button. Success toast: "Metric saved successfully."
- **Summary:** period slider (1–90 days); one **collapsible card per metric type** titled "Blood Pressure (12 entries)"; expanded shows up to the 5 latest entries as rows (date, value + unit, note).
- **Bulk Import:** explanatory text "Upload a CSV, JSON, or XML file containing your historical health logs", an info notice listing the expected columns `metric_type`, `value`, `unit` (optional), `date` (optional), a **drop-zone-style file picker** (accepts .csv, .json, .xml), and a **Process import** button that appears once a file is chosen. Result toast: success, or warning when some rows were skipped (message includes counts).

### 6.7 Medications (`/medications`)
Title "Medication Manager", description "Track your prescriptions, log doses, and set Google Calendar reminders." **3 tabs:** **My Medications**, **Add Medication**, **Adherence Report**.

- **My Medications** ("Active medications"): a list of medication cards. Each card: name (H3) + dosage, a calendar-reminder chip (**Reminder set** with a calendar-check icon in green, or **No reminder** with a calendar-x icon in neutral), a meta row (frequency, time of day, start date), notes (if any), and three actions: **Taken** (success-tinted secondary), **Skipped** (warning-tinted secondary), **Remove** (neutral, destructive on confirm). Empty: info notice prompting the user to add their first medication.
- **Remove confirmation** **[visual change]**: the app uses a browser confirm today. Design a modal: "Remove {name}?" / "Its Google Calendar reminder will be deleted too." / **Cancel** (secondary) and **Remove** (destructive).
- **Add Medication:** Name (required, placeholder "e.g. Metformin"), Time (time of day), Dosage (placeholder "e.g. 500mg"), Start date, Frequency select (Daily, Twice daily, Weekly, As needed), End date (optional), Notes (placeholder "e.g. Take with food"), **Add medication** primary button. After saving, toasts report success and whether the Google Calendar reminder was created (info) or failed ("login may need refresh", warning).
- **Adherence Report:** period slider (7–90 days, default 30). A hero card: "Overall adherence (last N days)", a large percentage, a status line (**Great** in green when ≥80%, **Needs improvement** in amber otherwise), a progress bar, and a stat row: Taken, Skipped, Not logged, "of N expected doses." Each stat has an icon and a number. Empty: "No adherence data yet. Add a medication and use the My Medications tab to log doses."

### 6.8 Legal pages (`/terms`, `/privacy`)
Narrow reading layout, 720px, H1, H2 sections, 16/26 body, a "Back to app" link, and a footer. Already text-only; design only typography and spacing.

### 6.9 System screens
- **Loading profile:** centered brand mark with a spinner and "Loading your profile…".
- **Profile load error:** centered error message with **Try again** (primary) and **Log out** (secondary).
- **Toasts:** bottom-right desktop, bottom-center above the tab bar on mobile. Four variants (success, error, warning, info).

### 6.10 Sample data for generating realistic screens
Name "Priya Sharma"; Heart rate 72 bpm (↓ −3); Blood pressure 118/76 (no change); Sleep 6.5 h (outside range, ↓ −0.5 h); Weight 68.4 kg (↓ −0.6 kg); goals "Lose 5kg, Sleep 8 hours daily, Walk 30 minutes"; medications Metformin 500 mg (twice daily, 08:00), Lisinopril 10 mg (daily, 21:00); adherence 86%.
Sample AI analysis: "Your heart rate and blood pressure are within healthy ranges. Sleep has averaged below 7 hours this week, which is worth watching. Your weight is trending down gently toward your goal."

---

## 7. Component specifications

### 7.1 Buttons (height 40px; 44px on mobile; small 32px)
| Variant | Fill | Text | Border | Use |
|---|---|---|---|---|
| Primary | `primary-600` | white | none | One per view area: Send, Save, Add, Login |
| Secondary | `surface` | `text` | 1px `border-strong` | Refresh, PDF Report, Logout, Taken/Skipped |
| Tertiary / text | transparent | `primary-600` | none | In-line links, "Go to Chat" |
| Destructive | `error-700` | white | none | Remove (in the confirm dialog only) |
Radius 10px, icon 18px left of label with 8px gap. **[visual change]** Drop today's gradient fill and glow shadow on primary buttons; use a flat fill.

### 7.2 Form fields
Label above (14/500), field 44px high, `surface` fill, 1px `border-strong`, radius 10px, 12px horizontal padding, 16px text (prevents iOS zoom). Helper text below in caption style. Select uses a chevron icon. Textarea min height 96px. Range slider: 4px track, 20px thumb, current value shown in the label. File input styled as a button plus filename. Checkbox/radio chips: 44px high, 1px border, selected = `primary-50` fill + `primary-600` border + check icon.

### 7.3 Cards
`surface`, 1px `border`, radius 16px, padding 24px. Variants: **Metric card** (overline + large value + change line + status chip), **AI insight card** (`secondary-50`, left accent bar, avatar), **List card** (medication), **Empty card** (centered icon, text, optional action; dashed border), **Collapsible card** (summary row with a chevron that rotates, 48px tap target).

### 7.4 Navigation items
Height 44px, radius 10px, 12px padding, icon + label. Default: `text-soft`. Hover: `surface-sunken`. Active: `primary-50` fill, `primary-700` text, 3px `primary-600` left indicator, `aria-current="page"`. Mobile tab bar: icon over label, active icon filled with `primary-600`.

### 7.5 Tabs
Underline tabs, 44px high. Active: `primary-600` text and a 2px bottom border. Inactive: `text-muted`; hover `text`. Horizontally scrollable on mobile. Implemented as `role="tablist"`.

### 7.6 Badges and chips
Height 24px, radius 999px, 12px/600 text, icon 14px. Variants: success, warning, error, info, neutral. Always icon + text. "ML POWERED" is neutral/info. Feature chips on the landing page use `primary-50` and neutral tints with an icon.

### 7.7 Status indicator
An 8px dot is **never used alone**. Use an icon + label chip (section 3.3), or a dot paired with visible text.

### 7.8 Tables
Header row `surface-sunken`, 12/600 uppercase `text-muted`. Rows 48px, 14px text, bottom border `border`, hover `bg`. Numeric columns tabular. The table scrolls horizontally inside its container on mobile. **[visual change]** On <640px, show Wellness log rows as stacked cards (date + metric on the first line, value on the second, notes below).

### 7.9 Charts (Recharts)
Card-wrapped, height 260px (220px mobile), 12px axis text, light horizontal gridlines only, 2px lines with 6px point markers on hover, rounded bar tops (4px). Tooltip: surface, 1px border, shadow, with date and value + unit. Legend only for multi-series (blood pressure). Provide a visually hidden data summary or table alternative for each chart.

### 7.10 Chat bubble, composer, typing indicator
Specified in 6.2. The typing indicator is 3 dots pulsing in 1.2s, or a static "Thinking…" when reduced motion is on.

### 7.11 Notices (inline)
Radius 12px, 1px border, icon + text, 14px. Info, success, warning, error use the 50 background and 700 text tokens. Errors that block a view state what failed and what to do.

### 7.12 Toasts
360px max, surface, 4px left bar in the variant color, icon + message, close button, auto-dismiss at 5s (errors persist until closed). `role="status"`, or `role="alert"` for errors.

### 7.13 Modal dialog
Used for the medication remove confirmation only. 440px wide, radius 16px, scrim `rgba(15,31,46,0.5)`, focus trapped, Esc closes, destructive action on the right.

### 7.14 Avatar
Circular 32–40px. User: initial on `primary-50`. Assistant: brand glyph on `secondary-600`.

---

## 8. Interaction states

| State | Rule |
|---|---|
| **Hover** | Buttons darken one step (primary → `primary-700`); secondary gets `surface-sunken`; cards with actions get `border-strong`. No movement or scaling. |
| **Focus (keyboard)** | 2px `primary-600` outline + 2px white offset ring on every interactive element; never remove outlines. Inputs also show a `primary-600` border. |
| **Active/pressed** | One step darker than hover. |
| **Disabled** | 45% opacity, `not-allowed` cursor, no hover. Explain why nearby when not obvious (for example Send is disabled while a reply is pending). |
| **Loading** | Skeleton blocks (shimmer 1.4s) for cards and tables; inline spinner in the button with the label changed ("Saving…", "Refreshing…", "Processing file…"); chat uses the typing indicator; the AI card shows "Analyzing your health data…". |
| **Empty** | Always icon + one sentence + the next action. Copy comes from the app: "No metrics logged yet…", "No health goals set yet…", "No adherence data yet…", chart empty prompts. |
| **Success** | Toast + (where relevant) updated data in place. File upload: success notice "'{file}' added to your knowledge base!" |
| **Validation** | Validate on submit; show the message under the field in `error-700` with an icon, set `aria-invalid`, and move focus to the first invalid field. Required fields: Onboarding (age, gender, height, weight, fitness level), medication name, metric value. Messages: "Medication name is required.", "Please enter a value." |
| **Error** | Inline notice for load failures ("Could not load health data: …"); toast for action failures; full-page message for profile load failure with Retry. Never show raw stack traces; keep the server message short. |
| **Upload** | idle (dashed drop area) → uploading ("Processing {file}…" with an indeterminate bar, input disabled) → done (success notice) or error ("Upload failed: …"). |
| **AI analysis** | pending, generated (success badge), failed (error badge "Check needed" with the message). Refresh disables during fetch. |
| **Motion** | 150–200ms ease-out for color/opacity; 200ms for collapsible expansion; honor `prefers-reduced-motion` by removing all non-essential motion. |

---

## 9. Responsive design

| Breakpoint | Behavior |
|---|---|
| **Desktop ≥1024px** | Sidebar 264px; 4-column vital cards; 2-column dashboard/goals rows; tables full width. |
| **Tablet 640–1023px** | Icon rail 72px; vital cards 2×2; Goals and Dashboard rows stack when a card's content would be narrower than 320px; forms stay 2-column. |
| **Mobile <640px** | Bottom tab bar; single-column everything except the vital 2×2 grid; forms 1-column; tabs scroll horizontally; tables become stacked cards; chat composer pinned above the tab bar; modals become bottom sheets; toasts above the tab bar. Touch targets ≥44×44px. |
| **Large ≥1440px** | Content stays capped at 1120px; the extra space is background. |

Design checkpoints: 1440, 1024, 768, 390 widths. No horizontal page scroll at any width.

---

## 10. Accessibility

- **Target WCAG 2.2 AA.** All text ≥4.5:1 (token values above were chosen for this); UI components and chart lines ≥3:1 against their background.
- **Keyboard:** every control reachable in logical order; skip-to-content link at the top; visible focus (section 8); tabs support arrow keys; the modal traps focus and returns it on close; the chat composer submits on Enter.
- **Color independence:** status always has an icon + text (section 3.3); chart series differ by more than color (line style or markers, plus a legend or direct labels).
- **Labels:** every input has a visible `<label>`; placeholders are examples only, not labels. Icon-only buttons (Send, close, avatar menu) have `aria-label`s. Groups use `<fieldset><legend>`.
- **Live regions:** toasts use `role="status"`/`"alert"`; the chat message list uses `aria-live="polite"` so new replies are announced; the AI analysis loading and result changes are announced.
- **Healthcare readability:** units always shown next to values; blood pressure always written `118/76 mmHg`; dates in an unambiguous format; no abbreviations without explanation on first use; line length ≤70 characters for AI text; minimum 16px body, 44px touch targets; support 200% zoom and text-spacing overrides without clipping.
- **Charts:** accessible name and a text summary (for example "Weight trend, 14 readings from 70.1 to 68.4 kg"), plus access to the underlying numbers.
- **Motion:** respect `prefers-reduced-motion`. No auto-playing animation longer than 5s.
- **Language:** `lang="en"`; plain-language copy (about grade 8).
- **Safety copy:** the AI is informational. Show the "general information, not medical advice" line in the chat composer area and the AI Analysis card footer.

---

## 11. Design consistency rules

1. **Tokens only.** Colors, type sizes, spacing, radii, and shadows come from sections 3–5. No ad-hoc values.
2. **One primary action per view area.** Everything else is secondary or tertiary.
3. **Same vocabulary everywhere.** Use "Metric" for a logged measurement, "Medication" (not "Medicine" or "Drug"), "Goal", "Reading" for the latest value. Page titles match nav labels (Chat, Dashboard, Goals, "Your Wellness Tracker" under Wellness, "Medication Manager" under Medications).
4. **Hierarchy:** page title (H1) → section (H2) → card title (H3/overline) → value. Large numbers are for the user's own health values only.
5. **Status system is global:** the same icons, colors, and labels for in range / outside range / no reference, and for success / warning / error across dashboard, medications, toasts, and notices.
6. **AI content is always marked:** the assistant avatar and the AI-insight card style appear only for model-generated text.
7. **Cards on `bg`, never cards on cards** (except a collapsible's inner rows).
8. **Icons:** one family, one stroke width, no emoji **[visual change]**.
9. **Forms:** label above, helper below, error below; the same 44px control height everywhere; the submit button is full width within a card and bottom-aligned on mobile.
10. **Charts:** same card, same axis style, same palette; `primary-500` is always the first series.
11. **Component variants are finite:** button (4), badge (5), notice (4), card (5), field (text, select, textarea, range, file, chip-group).
12. **Light and dark must be token swaps only.** No screen-specific dark overrides.

---

## 12. Stitch workflow

The Stitch MCP server exposes these tools: `create_project`, `list_projects`, `get_project`, `upload_design_md`, `create_design_system_from_design_md`, `create_design_system`, `update_design_system`, `list_design_systems`, `apply_design_system`, `generate_screen_from_text`, `generate_variants`, `edit_screens`, `list_screens`, `get_screen`, `delete_project`.

> I have not yet called any of these. The order below follows each tool's own description. `upload_design_md` is documented as the step before `create_design_system_from_design_md`, which takes a screen-instance ID. Confirm the exact return shape on the first call and adjust.

### Step 1 — Create the project
`create_project` with title **"HealthAgent"**. Keep the returned `projectId`.

### Step 2 — Turn this file into a design system
1. `upload_design_md` with `projectId` and the base64 of this file (`base64 -w 0 design.md`).
2. `create_design_system_from_design_md` with the `projectId`, the screen instance created by the upload, and `deviceType: DESKTOP`.
3. `list_design_systems` and record the design system's asset ID (like `assets/…`). **Every later screen must pass it as `designSystem`** so colors, type, and components stay consistent.

If the upload only picks up part of the file, fall back to `create_design_system` and paste sections 3–5 and 7 as the token and component definitions.

### Step 3 — Generate screens, one prompt each, in this order
Always set `designSystem`. Use `DESKTOP` first, then repeat the key screens as `MOBILE`. Start each prompt with: *"HealthAgent, a personal AI health companion. Light theme, calm and clinical. Follow the attached design system. Use sample data from design.md §6.10."* Then add the screen's section from §6.

| # | Prompt content | Device |
|---|---|---|
| 1 | Dashboard (§6.4) inside the app shell (§5.1) | Desktop, then Mobile |
| 2 | Chat with a populated conversation and the upload card (§6.2) | Desktop, Mobile |
| 3 | Wellness: View Logs with table + Add Metric state (§6.6) | Desktop, Mobile |
| 4 | Medications: My Medications list + Adherence Report (§6.7) | Desktop, Mobile |
| 5 | Goals with the three charts (§6.5) | Desktop |
| 6 | Onboarding (§6.3) | Desktop, Mobile |
| 7 | Landing with guest chat (§6.1) | Desktop, Mobile |
| 8 | States board: empty, loading, error, and toast variants (§8) | Desktop |
| 9 | Remove-medication confirm modal (§7.13) | Desktop |

Generation can take a few minutes. Do not retry on timeout; poll with `get_screen` every 30 seconds instead.

### Step 4 — Review and refine
- `list_screens` and `get_screen` to inspect results against this file: contrast, status icons next to every color, no emoji, no invented features (§1 "Not in the product").
- `edit_screens` for targeted fixes ("make the status chips icon + text", "reduce the card padding to 24px").
- `generate_variants` for the highest-risk screens (Dashboard, Chat) to compare layout options, then pick one and re-edit the others to match.
- `apply_design_system` to snap any off-token screen back to the system.
- If tokens need to change, edit this file, then `update_design_system`, and re-apply.

### Step 5 — Dark theme variant
After the light screens are approved, regenerate the Dashboard and Chat with the dark tokens (§3.2) to validate the token swap, then decide whether to ship dark.

### Step 6 — Hand off to implementation (a later task, not part of this one)
Export the approved screens and map the design tokens onto the `:root` variables in `web/src/index.css` (`--bg`, `--panel`, `--primary`, …). The existing structure (`.shell`, `.sidebar`, `.card`, `.btn`, `.badge`, `.notice`, `.tabs`) already matches the component names in §7, so the migration is mostly token values plus the changes marked **[visual change]**: Inter, icons instead of emoji, flat buttons, the mobile tab bar, and the modal.

### Definition of done for the design pass
- All 7 routes plus the system states exist in the Stitch project, in desktop and mobile where listed.
- Every screen uses the project design system, and no screen shows a feature from the "Not in the product" list.
- Contrast and status-icon checks in §10 pass on every screen.
