import os
import sys
import requests
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.services.ssi_service import SSIService

def test_single_ssi():
    ssi = SSIService()
    if ssi.login():
        print("Logged in")
        urls = [
            f"{ssi.base_url}/Market/SecuritiesDetails",
        ]
        
        results = {}
        for sym in ["VIC", "ASP", "VCB", "ACB"]:
            params = {
                "lookupRequest.symbol": sym,
                "lookupRequest.pageIndex": 1,
                "lookupRequest.pageSize": 10
            }
            try:
                res = requests.get(urls[0], headers=ssi._get_headers(), params=params)
                print(f"[{sym}] Status: {res.status_code}")
                if res.status_code == 200:
                    results[sym] = res.json()
                else:
                    results[sym] = res.text
            except Exception as e:
                results[sym] = str(e)
                
        with open("ssi_test_out.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
                
    else:
        print("Login failed")

if __name__ == "__main__":
    test_single_ssi()
