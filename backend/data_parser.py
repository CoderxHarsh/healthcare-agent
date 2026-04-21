import re
from .typing import Optional, Dict, List, Tuple

class HealthMetricParser:
    """Parse health metrics from natural language input"""

    # Define patterns for different health metrics
    METRIC_PATTERNS = {
        "blood_pressure": {
            "regex": r"(?:BP|blood pressure|bp)\s*(?:is|:)?\s*(\d+)\s*[/\\]\s*(\d+)",
            "unit": "mmHg",
            "value_formatter": lambda m: f"{m.group(1)}/{m.group(2)}"
        },
        "weight": {
            "regex": r"(?:weight|weigh)\s*(?:is|:)?\s*(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilogram|weighs?|lbs|pounds)",
            "unit": "kg",
            "value_formatter": lambda m: f"{m.group(1)}"
        },
        "blood_sugar": {
            "regex": r"(?:sugar|glucose|blood sugar|bs)\s*(?:is|:)?\s*(\d+(?:\.\d+)?)\s*(?:mg/dl|mmol|ml)",
            "unit": "mg/dL",
            "value_formatter": lambda m: f"{m.group(1)}"
        },
        "heart_rate": {
            "regex": r"(?:heart rate|pulse|bpm|hr)\s*(?:is|:)?\s*(\d+(?:\.\d+)?)",
            "unit": "bpm",
            "value_formatter": lambda m: f"{m.group(1)}"
        },
        "sleep": {
            "regex": r"(?:slept?|sleep)\s*(?:for)?\s*(\d+(?:\.\d+)?)\s*(?:hour|hrs|h|hour[s]?)",
            "unit": "hours",
            "value_formatter": lambda m: f"{m.group(1)}"
        },
        "exercise": {
            "regex": r"(?:walk|run|exercise|jog|cycling|swim|jogging|running|walked|ran)\s*(?:for)?\s*(\d+(?:\.\d+)?)\s*(?:min|minute|minutes|km|kms|mile)",
            "unit": "minutes",
            "value_formatter": lambda m: f"{m.group(1)}"
        },
        "temperature": {
            "regex": r"(?:temperature|temp|fever)\s*(?:is|:)?\s*(\d+(?:\.\d+)?)\s*(?:°C|°F|celsius|fahrenheit)",
            "unit": "°C",
            "value_formatter": lambda m: f"{m.group(1)}"
        }
    }

    @staticmethod
    def parse(user_input: str) -> List[Dict]:
        """
        Parse health metrics from user input.
        Returns a list of extracted metrics with their details.
        
        Example:
            "My BP is 120/80 and I slept 8 hours" 
            → [
                {"metric_type": "blood_pressure", "value": "120/80", "unit": "mmHg"},
                {"metric_type": "sleep", "value": "8", "unit": "hours"}
            ]
        """
        extracted_metrics = []
        input_lower = user_input.lower()

        for metric_type, pattern_info in HealthMetricParser.METRIC_PATTERNS.items():
            regex = pattern_info["regex"]
            match = re.search(regex, input_lower, re.IGNORECASE)
            
            if match:
                value = pattern_info["value_formatter"](match)
                extracted_metrics.append({
                    "metric_type": metric_type,
                    "value": value,
                    "unit": pattern_info["unit"]
                })

        return extracted_metrics

    @staticmethod
    def extract_and_format(user_input: str) -> str:
        """
        Extract metrics and return a formatted summary string.
        
        Example:
            "My BP is 120/80" → "📊 Extracted: Blood Pressure: 120/80 mmHg"
        """
        metrics = HealthMetricParser.parse(user_input)
        
        if not metrics:
            return "No health metrics found in your message."
        
        summary = "📊 Extracted health metrics:\n"
        for metric in metrics:
            metric_name = metric["metric_type"].replace("_", " ").title()
            summary += f"  • {metric_name}: {metric['value']} {metric['unit']}\n"
        
        return summary
