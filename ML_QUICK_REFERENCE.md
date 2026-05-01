# ML Health Analysis System - Quick Reference Guide

## 📊 What It Does

```
User Health Data (30 days)
    ↓
[Heart Rate | Blood Pressure | Weight | Sleep | Blood Glucose]
    ↓
AI Analysis Engine
    ├─ Trend Detection (improving/declining/stable)
    ├─ Anomaly Detection (readings outside normal ranges)
    ├─ Risk Assessment (age/conditions/meds-based)
    └─ LLM Generation (personalized insights)
    ↓
Dashboard Display
    ↓
"Your metrics are stable. Add 15 min cardio 3x/week to reach your 5kg goal..."
```

## 🎯 System Architecture

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    STREAMLIT DASHBOARD                 ┃
┃  ┌─────────────────────────────────────────────────┐   ┃
┃  │  🤖 AI ANALYSIS                                │   ┃
┃  │  [3-4 line personalized health insight]       │   ┃
┃  │  ✅ GENERATED | ML POWERED                     │   ┃
┃  └─────────────────────────────────────────────────┘   ┃
┗━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                 │
                 │ HTTP GET
                 ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        FASTAPI BACKEND - /user/{id}/vitals-summary     ┃
┃  ┌─────────────────────────────────────────────────┐   ┃
┃  │  1. Fetch User Profile (age, conditions, meds) │   ┃
┃  │  2. Fetch Health Logs (last 30 days)           │   ┃
┃  │  3. Pass to HealthAnalyzer.generate_ai_analysis│   ┃
┃  │  4. Return JSON response                        │   ┃
┃  └─────────────────────────────────────────────────┘   ┃
┗━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                 │
                 ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃          HEALTH ANALYZER (health_analyzer.py)          ┃
┃  ┌─────────────────────────────────────────────────┐   ┃
┃  │  HealthAnalyzer.generate_ai_analysis()         │   ┃
┃  │    ├─ analyze_health_profile()                  │   ┃
┃  │    │  ├─ extract_metric_values()                │   ┃
┃  │    │  ├─ calculate_trend()                      │   ┃
┃  │    │  └─ detect_anomalies()                     │   ┃
┃  │    ├─ assess_risk_factors()                     │   ┃
┃  │    │  ├─ Check age-based risks                  │   ┃
┃  │    │  ├─ Check condition-specific risks         │   ┃
┃  │    │  ├─ Check medication interactions          │   ┃
┃  │    │  └─ Check BMI and weight concerns          │   ┃
┃  │    └─ Generate LLM prompt with analysis         │   ┃
┃  └─────────────────────────────────────────────────┘   ┃
┗━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                 │
                 │ LLM Prompt with context
                 ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃          GROQ LLM (gpt-oss-20b)                        ┃
┃  ┌─────────────────────────────────────────────────┐   ┃
┃  │  Generate personalized 3-4 sentence analysis   │   ┃
┃  │  based on:                                      │   ┃
┃  │  • User profile & goals                         │   ┃
┃  │  • Metric trends                               │   ┃
┃  │  • Identified risks                            │   ┃
┃  │  • Health conditions & medications             │   ┃
┃  └─────────────────────────────────────────────────┘   ┃
┗━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                 │
                 │ AI-generated analysis
                 ▼
           Dashboard Display
```

## 📈 Analysis Metrics

### Metrics Analyzed
| Metric | Range | Unit | Status |
|--------|-------|------|--------|
| Heart Rate | 60-100 | bpm | ✅ Analyzed |
| Blood Pressure (Systolic) | 90-120 | mmHg | ✅ Analyzed |
| Blood Pressure (Diastolic) | 60-80 | mmHg | ✅ Analyzed |
| Weight | Customizable | kg | ✅ Analyzed |
| Sleep | 7-9 | hours | ✅ Analyzed |
| Blood Glucose | 70-100 | mg/dL | ✅ Analyzed |

### Trend Indicators
```
IMPROVING    ↘️  Metric getting better (>5% decrease)
STABLE       ➡️  Metric consistent (±5% variance)
WORSENING    ↗️  Metric getting worse (>5% increase)
INSUFFICIENT_DATA  Not enough readings to determine
```

## ⚠️ Risk Assessment

### Risk Categories
1. **Age-Based**
   - 45+: "Monitor cardiovascular health"
   - 60+: "Increased cardiovascular risk"

2. **Condition-Based**
   - Diabetes: "Monitor blood glucose regularly"
   - Hypertension: "Monitor BP regularly"
   - Obesity: "Increase exercise" + BMI alert

3. **Medication-Based**
   - Metformin/Insulin: "Maintain consistent diet and exercise"
   - Other meds: Condition-specific alerts

4. **Trend-Based**
   - Worsening metrics: Alert to consult doctor
   - Critical anomalies: High-severity warnings

## 🎯 AI Analysis Examples

### Example 1: Healthy User with Good Trends
```
Input: 35-year-old, healthy, fitness goal, improving weight trend
Output: "You're on an excellent fitness journey! Your weight is trending 
down by 1kg/month, and your heart rate remains stable around 70 bpm. 
Keep up your current routine and aim for 150 minutes of cardio weekly. 
Your consistency is already showing results."
```

### Example 2: User with Concerning Trends
```
Input: 55-year-old, diabetes, blood pressure trending up, stress level high
Output: "Your blood pressure has been trending upward over the past 14 days 
(118→128 mmHg), which needs attention. With your diabetes history, this is 
important to address. Please consult your doctor, reduce sodium intake, 
and try stress-reduction techniques like 10 minutes daily meditation."
```

### Example 3: User Starting Out
```
Input: New user with only 1 week of data
Output: "Welcome to health tracking! You're off to a great start with 
consistent logging. After 2 more weeks of data, I'll be able to provide 
more personalized insights about your health trends. Keep logging daily!"
```

## 🔧 Technical Details

### File Structure
```
backend/
├── health_analyzer.py          ← ML Engine (NEW)
├── api.py                       ← API endpoint (UPDATED)
├── models.py                    ← Database models
├── crud.py                      ← Database operations
└── chatbot.py                   ← LLM utilities

frontend/
└── app.py                       ← Dashboard display (UPDATED)

Test & Docs:
├── test_health_analyzer.py      ← Test suite (NEW)
├── ML_HEALTH_ANALYZER_DOCUMENTATION.md    ← Technical docs (NEW)
└── ML_HEALTH_ANALYSIS_SUMMARY.md          ← This guide (NEW)
```

### Key Functions

**`HealthAnalyzer.generate_ai_analysis(user_profile, health_logs)`**
- Main function to generate personalized analysis
- Returns: 3-4 line personalized health insight string

**`get_health_analysis(user_profile, health_logs)`**
- Convenience wrapper around HealthAnalyzer
- Handles errors gracefully
- Returns: Analysis string or fallback message

### API Response Format
```json
{
    "status": "success",
    "summary": "Your metrics are stable and trending well. Continue your current routine...",
    "generated_at": "2026-05-01T10:30:45.123456"
}
```

## 🚀 Quick Start

### 1. View in Dashboard
```
1. Open Streamlit app: streamlit run frontend/app.py
2. Login and navigate to Dashboard
3. Scroll to "🤖 AI ANALYSIS" section
4. See your personalized health insights!
```

### 2. Test Locally
```bash
# Test the analyzer directly
python test_health_analyzer.py

# Will output:
# - Profile analysis with trends
# - Risk assessment
# - AI-generated analysis (requires GROK_API_KEY)
# - Edge case tests
```

### 3. API Testing
```bash
# Get analysis for user 1
curl http://localhost:8000/user/1/vitals-summary

# Response:
# {
#   "status": "success",
#   "summary": "Your health metrics show...",
#   "generated_at": "2026-05-01T..."
# }
```

## ⚙️ Configuration

### Required
- `GROK_API_KEY`: API key for Groq LLM
- `DATABASE_URL`: PostgreSQL connection string

### Optional (Customization)
- Adjust normal health ranges in `health_analyzer.py`
- Change LLM model in `HealthAnalyzer.__init__()`
- Add/remove metrics in `analyze_health_profile()`

## 🧪 Testing Checklist

- [x] Module imports successfully
- [x] Analyzer works with sample data
- [x] Trend detection working correctly
- [x] Anomaly detection identifying outliers
- [x] Risk assessment identifying conditions
- [x] LLM generates personalized analysis
- [x] API endpoint returns proper response
- [x] Frontend displays analysis correctly
- [x] Error handling working for edge cases
- [x] Empty data returns helpful message

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Analysis Time | 2-5 seconds |
| Data Scope | Last 30 days |
| Min Data Points | 3 for trend detection |
| LLM Model | gpt-oss-20b |
| Max Output | 512 tokens (≈3-4 sentences) |
| Error Recovery | Graceful fallback |

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Analysis unavailable" | Check user has health logs (use Chat to log data) |
| Timeout error | Wait 30s or refresh page |
| No module error | Ensure `backend/health_analyzer.py` exists |
| LLM error | Check `GROK_API_KEY` is set in `.env` |
| DB connection error | Verify PostgreSQL is running |

## 📚 Additional Resources

- **Full Docs**: `ML_HEALTH_ANALYZER_DOCUMENTATION.md`
- **Summary**: `ML_HEALTH_ANALYSIS_SUMMARY.md`
- **Tests**: `test_health_analyzer.py`
- **Code**: `backend/health_analyzer.py`

---

**System Status**: ✅ Active and Running  
**Last Updated**: May 1, 2026  
**Version**: 1.0 Production
