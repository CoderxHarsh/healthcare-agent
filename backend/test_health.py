"""
API Health Check Test
=====================
Verifies FastAPI server is running and configuration is correct.
Checks OAuth and database status through the /health endpoint.

Run from: python test_health.py (requires FastAPI server running on port 8000)
"""

# requests - HTTP client for making API calls
import requests
# json - JSON formatting for display
import json

try:
    print("🔄 Testing API health endpoint...")
    response = requests.get("http://localhost:8000/health", timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Health check successful!")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Error: Status code {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error connecting to API: {str(e)}")
