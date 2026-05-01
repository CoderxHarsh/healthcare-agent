# ML Health Analysis System Documentation

## Overview
The ML Health Analysis system uses machine learning and AI to generate personalized, 3-4 line health insights for each user based on their health data stored in PostgreSQL and retrieved from the vector database (Chroma).

## Architecture

### Components

#### 1. **Health Analyzer Module** (`backend/health_analyzer.py`)
The core ML engine that analyzes user health data:

- **Statistical Analysis**: Detects trends in vital signs (improving/declining/stable)
- **Anomaly Detection**: Identifies readings outside normal ranges with severity levels
- **Risk Assessment**: Evaluates health risks based on:
  - Age and demographics
  - Existing health conditions
  - Current medications
  - Health metrics trends
- **LLM-based Insights**: Uses Groq LLM to generate personalized, human-readable analysis

### Key Classes

#### `HealthAnalyzer`
Main class for health analysis with methods:

- `extract_metric_values()`: Extract numeric values from health logs for a specific metric
- `calculate_trend()`: Determine if metric is improving, declining, or stable
- `detect_anomalies()`: Find readings outside normal ranges
- `analyze_health_profile()`: Comprehensive analysis of user health data
- `assess_risk_factors()`: Identify health risks and alert conditions
- `generate_ai_analysis()`: Create personalized 3-4 line health summary using LLM

### Normal Health Ranges (Configurable)
```python
{
    "heart_rate": {"min": 60, "max": 100, "unit": "bpm"},
    "blood_pressure_systolic": {"min": 90, "max": 120, "unit": "mmHg"},
    "blood_pressure_diastolic": {"min": 60, "max": 80, "unit": "mmHg"},
    "weight": {"min": 0, "max": 200, "unit": "kg"},
    "sleep": {"min": 7, "max": 9, "unit": "hours"},
    "blood_glucose": {"min": 70, "max": 100, "unit": "mg/dL"},
}
```

## Backend API Integration

### Endpoint: `/user/{user_id}/vitals-summary`
**Method**: GET  
**Purpose**: Generate ML-powered AI analysis of user's health

**Response**:
```json
{
    "status": "success",
    "summary": "Your heart rate has been stable around 75 bpm with good sleep patterns of 7-8 hours. However, your blood pressure readings show a slight upward trend—continue monitoring and consider reducing sodium intake. Overall, maintain your current fitness routine and stay consistent with your water intake.",
    "generated_at": "2026-05-01T10:30:45.123456"
}
```

**Error Response**:
```json
{
    "status": "error",
    "summary": "Unable to generate analysis at this moment. Please try again later.",
    "error": "..."
}
```

## Frontend Integration

### Dashboard AI Analysis Display
Located in `frontend/app.py` on the Dashboard page (around line 710):

**Features**:
- Real-time loading indicator during analysis generation
- Error handling with user-friendly messages
- AI-generated insights specific to each user
- Status badges ("✅ GENERATED" or "⚠️ CHECK NEEDED")
- Timeout handling with fallback messages

**Display Elements**:
```
🤖 AI ANALYSIS
[3-4 lines of personalized health insights from ML model]
✅ GENERATED  |  ML POWERED
```

## Data Flow

```
User Health Data (PostgreSQL)
  ↓
Health Logs (metrics: HR, BP, weight, sleep, etc.)
  ↓
HealthAnalyzer.analyze_health_profile()
  ├─ Extract metric values → [values]
  ├─ Calculate trends → improving/declining/stable
  ├─ Detect anomalies → [severity, range violations]
  └─ Assess risk factors → [risks based on age, conditions, meds]
  ↓
Groq LLM (gpt-oss-20b)
  ↓
Personalized AI Analysis (3-4 sentences)
  ↓
Frontend Dashboard
```

## Analysis Generation Process

### Step 1: Data Extraction
- Fetch user profile (age, gender, conditions, medications, goals)
- Fetch recent health logs (last 30 days)
- Extract values for key metrics

### Step 2: Trend Analysis
```
values = [72, 75, 73, 78, 80, 82]
         ↓
First half avg: 73.3
Second half avg: 80
         ↓
Change: +9.5% → WORSENING
```

### Step 3: Anomaly Detection
- Compare readings against normal ranges
- Flag high-severity anomalies (>20 units outside range)
- Include in risk assessment

### Step 4: Risk Assessment
Evaluates:
- Age-related cardiovascular risk (45+, 60+)
- Condition-specific risks (diabetes, hypertension)
- Medication interactions
- BMI/weight concerns
- Trend-based concerns

### Step 5: LLM Generation
Sends analysis context to Groq LLM with:
- User profile (name, age, goals, conditions)
- Recent metric readings
- Trend information
- Risk factors identified

LLM generates 3-4 sentences that are:
- Personalized and encouraging
- Practical and actionable
- Free of medical jargon
- Alert-focused when issues detected

## Configuration

### Environment Variables Required
```
GROK_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:pass@localhost/healthcare
```

### Customization Points

**1. Normal Ranges**: Edit in `HealthAnalyzer.__init__()`:
```python
self.normal_ranges = {
    "heart_rate": {"min": 60, "max": 100, "unit": "bpm"},
    # Customize per user if needed
}
```

**2. Metric Types to Analyze**: Edit in `analyze_health_profile()`:
```python
metrics_to_analyze = [
    "heart_rate",
    "blood_pressure",
    "weight",
    "sleep",
    "blood_glucose"
]
```

**3. LLM Model**: Change in `HealthAnalyzer.__init__()`:
```python
self.model = ChatGroq(
    model="openai/gpt-oss-20b",  # Change model here
    temperature=0.5,
    max_tokens=512
)
```

## Error Handling

The system gracefully handles:
- **No health logs**: Returns message prompting user to log data
- **LLM timeout**: Falls back to statistical summary
- **Missing profile data**: Uses available data for analysis
- **API timeouts**: Shows friendly error in frontend
- **Database errors**: Returns error status with user-friendly message

## Performance Considerations

- **Analysis Time**: ~2-5 seconds (mostly LLM inference)
- **Data Scope**: Last 30 days of health data
- **Caching**: Could be added to cache analysis for 1 hour
- **Scaling**: Each request fetches fresh data (ensures accuracy)

## Example Outputs

### Healthy User with Good Trends
```
Your heart rate has been stable around 75 bpm with consistent sleep of 7-8 hours nightly. 
Your weight remains steady at 68 kg, indicating good lifestyle management. 
Keep up your current fitness routine and continue logging your vitals to track long-term patterns.
```

### User with Concerning Trends
```
Your heart rate has been trending upward over the past two weeks (72→82 bpm), which warrants attention. 
Blood pressure is also slightly elevated at 128/85 mmHg. 
Please consult your doctor about these trends and consider reducing caffeine intake and increasing exercise frequency.
```

### User with Insufficient Data
```
No health data available. Start logging your vitals to get personalized insights. 
Track metrics like heart rate, blood pressure, weight, and sleep to receive AI-powered health analysis.
```

## Testing

### Import Test
```bash
python -c "from backend.health_analyzer import HealthAnalyzer; print('✅ HealthAnalyzer imported successfully')"
```

### Manual Testing
```python
from backend.health_analyzer import get_health_analysis

user_profile = {
    "name": "John Doe",
    "age": 45,
    "gender": "Male",
    "health_conditions": "Type 2 Diabetes",
    "medications": "Metformin 500mg",
    "health_goals": "Lose 5 kg, improve fitness"
}

health_logs = [
    {"metric_type": "heart_rate", "value": "72", "created_at": "2026-04-30T10:00:00"},
    {"metric_type": "blood_pressure", "value": "120/80", "created_at": "2026-04-30T10:00:00"},
    # ... more logs
]

analysis = get_health_analysis(user_profile, health_logs)
print(analysis)
```

## Future Enhancements

1. **Trend Predictions**: Use time-series ML to predict future metric values
2. **Pattern Recognition**: Identify recurring health patterns (time-of-day, day-of-week effects)
3. **Personalized Recommendations**: Generate specific exercise/diet recommendations based on data
4. **Medication Interaction Alerts**: Check medication interactions using vector search
5. **Goal Progress Tracking**: Measure progress toward user-defined health goals
6. **Comparative Analytics**: Compare user metrics against population averages
7. **Caching Layer**: Cache analysis for 1 hour to reduce LLM calls
8. **Custom ML Models**: Train custom models for specific conditions
9. **Real-time Alerts**: Alert users when readings exceed safe thresholds
10. **Historical Analysis**: Show how user's health has improved/declined over months

## Files Modified

- `backend/health_analyzer.py` - **NEW** - ML analysis engine
- `backend/api.py` - Updated `/user/{user_id}/vitals-summary` endpoint
- `frontend/app.py` - Enhanced AI ANALYSIS display with better error handling

## Status
✅ **Production Ready** - The system is fully functional and deployed to the dashboard.
