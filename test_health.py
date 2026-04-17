import requests
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
