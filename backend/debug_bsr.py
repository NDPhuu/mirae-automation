import os
import sys
import json
from datetime import datetime, timedelta

# Mock environment setup for standalone
os.environ["SSI_FC_URL"] = "https://fc-data.ssi.com.vn/api/v2"
os.environ["SSI_CONSUMER_ID"] = "AByRjG3XN93vAtWvK0rU/qCg2E29HjXUeE1X7e27eX7e" # I need to be careful with secrets, but I don't have access to the actual .env easily here
# Alternative: Load from the actual .env
from dotenv import load_dotenv
load_dotenv("d:\\WORKS\\Project\\mirae-automation\\backend\\.env")

# Adjust path for imports
sys.path.append("d:\\WORKS\\Project\\mirae-automation\\backend")
from src.services.ssi_service import SSIService

def debug_bsr():
    print("--- Debugging BSR SSI Data ---")
    s = SSIService()
    if not s.login():
        print("Login failed")
        return

    symbol = "BSR"
    url = f"{s.base_url}/Market/DailyStockPrice"
    today = datetime.now()
    from_date_str = (today - timedelta(days=10)).strftime("%d/%m/%Y")
    to_date_str = today.strftime("%d/%m/%Y")
    
    params = {
        "lookupRequest.symbol": symbol,
        "lookupRequest.fromDate": from_date_str,
        "lookupRequest.toDate": to_date_str,
        "lookupRequest.pageIndex": 1,
        "lookupRequest.pageSize": 10
    }
    
    import requests
    headers = s._get_headers()
    print(f"Requesting: {url} with params {params}")
    response = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    debug_bsr()
