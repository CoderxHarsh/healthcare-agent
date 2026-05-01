import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
from pdf_generator import generate_health_report_pdf

report_data = {
    'user_name': 'Test User',
    'age': 30,
    'gender': 'Male',
    'height_cm': 180,
    'weight_kg': 75,
    'bmi': 23.1,
    'bmi_category': 'Normal',
    'fitness_level': 'Active',
    'allergies': 'None',
    'health_conditions': 'None',
    'health_goals': True,
    'health_goals_list': ['Get fit', 'Sleep better'],
    'medications': [
        {'name': 'Aspirin', 'dosage': '100mg', 'frequency': 'daily', 'adherence_rate': 90}
    ],
    'past_medications': [
        {'name': 'Ibuprofen', 'dosage': '200mg', 'frequency': 'twice daily'},
        {'name': 'Vitamin D', 'dosage': '1000IU', 'frequency': 'daily'},
    ],
    'metrics_summary': [
        {'label': 'Weight', 'value': '75', 'unit': 'kg'}
    ],
    'health_logs': [
        {'date': '2026-04-19', 'metric_type': 'Weight', 'value': '75', 'unit': 'kg', 'notes': 'Feeling good'}
    ],
    'report_id': 'TEST1234'
}

try:
    result = generate_health_report_pdf(report_data)
    print(f"SUCCESS - PDF size: {len(result.getvalue())} bytes")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"FAILED: {e}")
