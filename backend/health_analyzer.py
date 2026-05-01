"""
Health Analyzer - ML-based health insights and predictions
===========================================================
Analyzes user health data to generate personalized AI insights using:
- Statistical trend analysis (improving/declining metrics)
- Risk factor assessment based on health conditions, age, medications
- Goal progress tracking
- Anomaly detection in vital signs
- LLM-based personalized health summary generation
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Load .env from root directory
env_path = find_dotenv() or Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from langchain_groq import ChatGroq

# ============================================
# HEALTH ANALYZER CLASS
# ============================================

class HealthAnalyzer:
    """
    Analyzes user health data and generates ML-powered health insights.
    Uses statistical analysis + LLM for personalized recommendations.
    """
    
    def __init__(self):
        """Initialize the analyzer with LLM model"""
        api_key = os.getenv("GROK_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GROK_API_KEY in environment variables")
        
        self.model = ChatGroq(
            model="openai/gpt-oss-20b",
            api_key=api_key,
            temperature=0.5,
            max_tokens=512
        )
        
        # Define normal ranges for common health metrics (can be customized per user)
        self.normal_ranges = {
            "heart_rate": {"min": 60, "max": 100, "unit": "bpm"},
            "blood_pressure_systolic": {"min": 90, "max": 120, "unit": "mmHg"},
            "blood_pressure_diastolic": {"min": 60, "max": 80, "unit": "mmHg"},
            "weight": {"min": 0, "max": 200, "unit": "kg"},  # Customizable per user
            "sleep": {"min": 7, "max": 9, "unit": "hours"},
            "blood_glucose": {"min": 70, "max": 100, "unit": "mg/dL"},  # Fasting
        }
    
    def extract_metric_values(
        self, 
        health_logs: List[Dict],
        metric_type: str,
        days: int = 30
    ) -> Tuple[List[float], List[str]]:
        """
        Extract numeric values and dates for a specific metric from health logs.
        
        Args:
            health_logs: List of health log entries
            metric_type: Type of metric to extract (e.g., "heart_rate", "weight")
            days: Only include logs from last N days
            
        Returns:
            Tuple of (values, dates)
        """
        values = []
        dates = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for log in health_logs:
            if log.get("metric_type") != metric_type:
                continue
            
            try:
                log_date = datetime.fromisoformat(log.get("created_at", ""))
                if log_date < cutoff_date:
                    continue
                
                # Parse value (handle cases like "120/80" for blood pressure)
                value_str = str(log.get("value", "")).split("/")[0]
                value = float(value_str)
                
                values.append(value)
                dates.append(log.get("created_at", "")[:10])
            except (ValueError, TypeError, IndexError):
                continue
        
        return values, dates
    
    def calculate_trend(self, values: List[float]) -> str:
        """
        Determine if a metric is improving, declining, or stable.
        
        Args:
            values: List of metric values (chronologically ordered)
            
        Returns:
            "improving", "declining", "stable", or "insufficient_data"
        """
        if len(values) < 3:
            return "insufficient_data"
        
        # Compare first third vs last third
        mid = len(values) // 2
        first_half = values[:mid]
        second_half = values[mid:]
        
        if not first_half or not second_half:
            return "insufficient_data"
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        # Calculate percentage change
        pct_change = ((second_avg - first_avg) / first_avg * 100) if first_avg != 0 else 0
        
        if pct_change > 5:  # More than 5% increase
            return "worsening"
        elif pct_change < -5:  # More than 5% decrease
            return "improving"
        else:
            return "stable"
    
    def detect_anomalies(self, values: List[float], metric_type: str) -> List[Dict]:
        """
        Detect anomalous readings using statistical methods.
        
        Args:
            values: List of metric values
            metric_type: Type of metric (for normal range lookup)
            
        Returns:
            List of anomalies with details
        """
        anomalies = []
        
        if len(values) < 2:
            return anomalies
        
        # Get normal range
        normal_range = self.normal_ranges.get(metric_type)
        if not normal_range:
            return anomalies  # No known normal range
        
        min_val = normal_range["min"]
        max_val = normal_range["max"]
        
        # Find values outside normal range
        for i, value in enumerate(values):
            if value < min_val or value > max_val:
                severity = "high" if value < min_val - 20 or value > max_val + 20 else "moderate"
                anomalies.append({
                    "value": value,
                    "index": i,
                    "severity": severity,
                    "outside_range": f"{min_val}-{max_val}"
                })
        
        return anomalies
    
    def analyze_health_profile(
        self,
        user_profile: Dict,
        health_logs: List[Dict]
    ) -> Dict:
        """
        Analyze user health profile and logs to extract key insights.
        
        Args:
            user_profile: User onboarding profile data
            health_logs: List of recent health logs
            
        Returns:
            Dict with analyzed metrics and trends
        """
        analysis = {
            "age": user_profile.get("age"),
            "gender": user_profile.get("gender"),
            "health_conditions": user_profile.get("health_conditions", ""),
            "current_medications": user_profile.get("medications", ""),
            "health_goals": user_profile.get("health_goals", ""),
            "fitness_level": user_profile.get("fitness_level", ""),
            "weight_kg": user_profile.get("weight_kg"),
            "height_cm": user_profile.get("height_cm"),
            "metric_trends": {},
            "anomalies": {},
            "recent_readings": {}
        }
        
        # Analyze key metrics
        metrics_to_analyze = [
            "heart_rate",
            "blood_pressure",
            "weight",
            "sleep",
            "blood_glucose"
        ]
        
        for metric in metrics_to_analyze:
            values, dates = self.extract_metric_values(health_logs, metric, days=30)
            
            if values:
                analysis["metric_trends"][metric] = {
                    "trend": self.calculate_trend(values),
                    "latest": values[-1],
                    "average": statistics.mean(values),
                    "count": len(values)
                }
                analysis["recent_readings"][metric] = {
                    "value": values[-1],
                    "date": dates[-1] if dates else None
                }
                
                # Detect anomalies
                anomalies = self.detect_anomalies(values, metric)
                if anomalies:
                    analysis["anomalies"][metric] = anomalies
        
        return analysis
    
    def assess_risk_factors(self, analysis: Dict) -> List[str]:
        """
        Assess health risk factors based on age, conditions, medications, and metrics.
        
        Args:
            analysis: Result from analyze_health_profile()
            
        Returns:
            List of risk factor descriptions
        """
        risk_factors = []
        
        age = analysis.get("age")
        conditions = analysis.get("health_conditions", "").lower()
        
        # Age-based risk assessment
        if age and age >= 60:
            risk_factors.append("Age-related: Increased cardiovascular risk (60+)")
        elif age and age >= 45:
            risk_factors.append("Age-related: Monitor cardiovascular health (45+)")
        
        # Condition-based risk assessment
        if "diabetes" in conditions:
            risk_factors.append("Diabetes: Monitor blood glucose regularly")
            if "heart_rate" in analysis.get("metric_trends", {}):
                hr_trend = analysis["metric_trends"]["heart_rate"]["trend"]
                if hr_trend == "worsening":
                    risk_factors.append("⚠️ Heart rate worsening - consult doctor")
        
        if "hypertension" in conditions or "high blood pressure" in conditions:
            risk_factors.append("Hypertension: Monitor BP regularly")
        
        if "obesity" in conditions or (analysis.get("weight_kg") and analysis.get("height_cm")):
            # Calculate BMI if available
            weight = analysis.get("weight_kg")
            height = analysis.get("height_cm")
            if weight and height:
                bmi = weight / ((height / 100) ** 2)
                if bmi > 30:
                    risk_factors.append(f"Obesity: BMI {bmi:.1f} - increase exercise")
                elif bmi > 25:
                    risk_factors.append(f"Overweight: BMI {bmi:.1f} - consider fitness plan")
        
        # Medication-based risk assessment
        meds = analysis.get("current_medications", "").lower()
        if "metformin" in meds or "insulin" in meds:
            risk_factors.append("Diabetes medication: Maintain consistent diet and exercise")
        
        # Anomaly-based alerts
        anomalies = analysis.get("anomalies", {})
        for metric, anomaly_list in anomalies.items():
            for anomaly in anomaly_list:
                if anomaly["severity"] == "high":
                    risk_factors.append(
                        f"🚨 {metric} reading is critically abnormal: {anomaly['value']}"
                    )
        
        return risk_factors
    
    def generate_ai_analysis(
        self,
        user_profile: Dict,
        health_logs: List[Dict]
    ) -> str:
        """
        Generate personalized 3-4 line AI analysis using LLM.
        
        Args:
            user_profile: User onboarding profile
            health_logs: Recent health logs
            
        Returns:
            3-4 line personalized health analysis string
        """
        if not health_logs:
            return "No health data available. Start logging your vitals to get personalized insights."
        
        # Analyze the health profile
        analysis = self.analyze_health_profile(user_profile, health_logs)
        
        # Assess risk factors
        risk_factors = self.assess_risk_factors(analysis)
        
        # Build context for LLM
        name = user_profile.get("name", "User")
        age = analysis.get("age", "")
        gender = analysis.get("gender", "")
        goals = analysis.get("health_goals", "")
        conditions = analysis.get("health_conditions", "")
        
        recent_readings = analysis.get("recent_readings", {})
        readings_text = "\n".join([
            f"- {metric}: {data['value']} ({data['date']})"
            for metric, data in recent_readings.items()
        ])
        
        trends_text = "\n".join([
            f"- {metric}: {data['trend']}"
            for metric, data in analysis.get("metric_trends", {}).items()
        ])
        
        risk_text = "\n".join(risk_factors) if risk_factors else "No major risk factors detected"
        
        prompt = f"""You are a healthcare AI assistant. Generate a SHORT, personalized health analysis (3-4 lines max) for {name}.

**User Profile:**
- Age: {age}, Gender: {gender}
- Health Goals: {goals}
- Existing Conditions: {conditions}

**Recent Health Metrics:**
{readings_text}

**Health Trends (improving/declining/stable):**
{trends_text}

**Risk Assessment:**
{risk_text}

REQUIREMENTS:
- Generate EXACTLY 3-4 sentences (not bullet points)
- Be positive and encouraging
- If trends are improving, celebrate that
- If anomalies exist, suggest consulting a doctor
- If no issues, reinforce good habits
- Keep it practical and actionable
- NO medical jargon

Analysis:"""

        try:
            response = self.model.invoke(prompt)
            analysis_text = response.content.strip()
            
            # Ensure it's 3-4 lines
            sentences = analysis_text.split(". ")
            if len(sentences) > 4:
                analysis_text = ". ".join(sentences[:4]) + "."
            
            return analysis_text
        except Exception as e:
            print(f"LLM error: {e}")
            # Fallback to statistical summary if LLM fails
            trend_summary = ", ".join([
                f"{metric} is {data['trend']}"
                for metric, data in analysis.get("metric_trends", {}).items()
                if data.get("trend") != "insufficient_data"
            ])
            
            if trend_summary:
                return f"Your health metrics show: {trend_summary}. Keep monitoring your vitals and maintain your current routine. Consult a doctor if any readings seem unusual."
            else:
                return "Keep logging your health data consistently for personalized insights. Regular tracking helps us understand your health patterns better."


# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_health_analysis(user_profile: Dict, health_logs: List[Dict]) -> str:
    """
    Convenience function to get health analysis from profile and logs.
    
    Args:
        user_profile: User profile dictionary
        health_logs: List of health log entries
        
    Returns:
        Personalized health analysis string
    """
    try:
        analyzer = HealthAnalyzer()
        return analyzer.generate_ai_analysis(user_profile, health_logs)
    except Exception as e:
        print(f"Health analysis error: {e}")
        return "Unable to generate analysis at this moment. Please try again later."
