import requests
import json

url = "http://localhost:8000/api/v1/report/generate"
payload = {
    "manual_override": {
        "expert_comment": "Test AI Report Generation after Sync v2 implementation"
    }
}

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Success! AI Report Sample:")
        print(response.json().get("report_content", "")[:500] + "...")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Failed to connect: {e}")
