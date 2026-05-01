"""
Test script for ML Health Analyzer
==================================
Demonstrates how the health analyzer works with sample user data.
Run this to verify the system is working correctly.
"""

import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from health_analyzer import HealthAnalyzer, get_health_analysis

def generate_sample_health_logs():
    """Generate sample health log data for testing."""
    base_date = datetime.now() - timedelta(days=30)
    logs = []
    
    # Heart rate logs (trending upward)
    for i in range(15):
        date = (base_date + timedelta(days=i*2)).isoformat()
        hr = 72 + (i * 0.5)  # Trending upward
        logs.append({
            "metric_type": "heart_rate",
            "value": str(int(hr)),
            "unit": "bpm",
            "created_at": date,
            "notes": ""
        })
    
    # Blood pressure logs (stable)
    for i in range(12):
        date = (base_date + timedelta(days=i*2.5)).isoformat()
        systolic = 118 + (i % 4 - 2)  # Fluctuate slightly
        diastolic = 78 + (i % 3 - 1)
        logs.append({
            "metric_type": "blood_pressure",
            "value": f"{systolic}/{diastolic}",
            "unit": "mmHg",
            "created_at": date,
            "notes": ""
        })
    
    # Weight logs (improving trend)
    for i in range(12):
        date = (base_date + timedelta(days=i*2.5)).isoformat()
        weight = 75 - (i * 0.3)  # Trending downward (weight loss)
        logs.append({
            "metric_type": "weight",
            "value": str(round(weight, 1)),
            "unit": "kg",
            "created_at": date,
            "notes": ""
        })
    
    # Sleep logs (good consistency)
    for i in range(14):
        date = (base_date + timedelta(days=i*2)).isoformat()
        sleep_hours = 7.5 + (i % 3 - 1) * 0.5  # 6.5-8.5 hours
        logs.append({
            "metric_type": "sleep",
            "value": str(round(sleep_hours, 1)),
            "unit": "hours",
            "created_at": date,
            "notes": "Good sleep quality"
        })
    
    return logs


def test_health_analyzer():
    """Test the health analyzer with sample data."""
    
    print("=" * 70)
    print("🧪 ML HEALTH ANALYZER TEST")
    print("=" * 70)
    
    # Sample user profile
    user_profile = {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "age": 45,
        "gender": "Male",
        "height_cm": 180,
        "weight_kg": 75,
        "health_conditions": "Type 2 Diabetes, Hypertension",
        "medications": "Metformin 500mg, Lisinopril 10mg",
        "allergies": "Penicillin",
        "fitness_level": "Moderate",
        "health_goals": "Lose 5 kg, improve fitness, manage diabetes better"
    }
    
    # Generate sample health logs
    health_logs = generate_sample_health_logs()
    
    print("\n📊 TEST SCENARIO")
    print("-" * 70)
    print(f"User: {user_profile['name']} (Age: {user_profile['age']}, Gender: {user_profile['gender']})")
    print(f"Conditions: {user_profile['health_conditions']}")
    print(f"Medications: {user_profile['medications']}")
    print(f"Health Goals: {user_profile['health_goals']}")
    print(f"\nHealth Data Points: {len(health_logs)}")
    
    # Count data by metric
    metric_counts = {}
    for log in health_logs:
        metric = log['metric_type']
        metric_counts[metric] = metric_counts.get(metric, 0) + 1
    
    print("\nMetric Distribution:")
    for metric, count in sorted(metric_counts.items()):
        print(f"  • {metric}: {count} readings")
    
    # Test the analyzer
    print("\n" + "=" * 70)
    print("🔍 ANALYZING HEALTH DATA...")
    print("=" * 70)
    
    try:
        analyzer = HealthAnalyzer()
        
        # Step 1: Analyze profile
        print("\n1️⃣  PROFILE ANALYSIS")
        print("-" * 70)
        analysis = analyzer.analyze_health_profile(user_profile, health_logs)
        
        print("\nMetric Trends:")
        for metric, trend_data in analysis.get("metric_trends", {}).items():
            trend = trend_data.get("trend")
            latest = trend_data.get("latest")
            average = trend_data.get("average")
            count = trend_data.get("count")
            print(f"  📈 {metric}:")
            print(f"     - Trend: {trend.upper()}")
            print(f"     - Latest: {latest}")
            print(f"     - Average: {average:.1f}")
            print(f"     - Data points: {count}")
        
        # Step 2: Risk assessment
        print("\n2️⃣  RISK ASSESSMENT")
        print("-" * 70)
        risk_factors = analyzer.assess_risk_factors(analysis)
        if risk_factors:
            print("\nIdentified Risk Factors:")
            for i, risk in enumerate(risk_factors, 1):
                print(f"  {i}. {risk}")
        else:
            print("✅ No significant risk factors detected")
        
        # Step 3: Generate AI analysis
        print("\n3️⃣  AI ANALYSIS GENERATION")
        print("-" * 70)
        print("\n🤖 Generating personalized AI analysis using Groq LLM...")
        
        ai_analysis = get_health_analysis(user_profile, health_logs)
        
        print("\n" + "=" * 70)
        print("✨ AI ANALYSIS RESULT")
        print("=" * 70)
        print(f"\n{ai_analysis}\n")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("=" * 70)
    print("✅ TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)
    return True


def test_edge_cases():
    """Test edge cases and error conditions."""
    
    print("\n\n" + "=" * 70)
    print("🧪 EDGE CASE TESTING")
    print("=" * 70)
    
    analyzer = HealthAnalyzer()
    
    # Test 1: Empty health logs
    print("\nTest 1: Empty Health Logs")
    print("-" * 70)
    empty_profile = {"name": "Jane Doe", "age": 30, "gender": "Female"}
    result = get_health_analysis(empty_profile, [])
    print(f"Result: {result[:100]}...")
    
    # Test 2: Insufficient data (< 3 points)
    print("\nTest 2: Insufficient Data Points")
    print("-" * 70)
    minimal_logs = [
        {
            "metric_type": "heart_rate",
            "value": "72",
            "unit": "bpm",
            "created_at": datetime.now().isoformat()
        }
    ]
    analysis = analyzer.analyze_health_profile(empty_profile, minimal_logs)
    print(f"Trend status: {analysis['metric_trends'].get('heart_rate', {}).get('trend', 'N/A')}")
    
    # Test 3: Anomalous readings
    print("\nTest 3: Anomalous Readings Detection")
    print("-" * 70)
    anomaly_logs = [
        {
            "metric_type": "heart_rate",
            "value": "45",  # Below normal
            "unit": "bpm",
            "created_at": (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            "metric_type": "heart_rate",
            "value": "120",  # Above normal
            "unit": "bpm",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    anomalies = analyzer.detect_anomalies([45, 120], "heart_rate")
    print(f"Anomalies detected: {len(anomalies)}")
    for anomaly in anomalies:
        print(f"  • Value {anomaly['value']} (severity: {anomaly['severity']})")
    
    print("\n✅ Edge case testing completed")


if __name__ == "__main__":
    # Run main test
    success = test_health_analyzer()
    
    # Run edge case tests
    if success:
        test_edge_cases()
    
    print("\n" + "=" * 70)
    print("📋 TESTING COMPLETE")
    print("=" * 70)
    print("\nTo test the full API endpoint, run the backend:")
    print("  python backend/api.py")
    print("\nThen in another terminal:")
    print("  curl http://localhost:8000/user/1/vitals-summary")
    print("\nOr test with the Streamlit frontend:")
    print("  streamlit run frontend/app.py")
