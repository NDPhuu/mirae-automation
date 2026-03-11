import os
import sys
import requests
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.services.ssi_service import SSIService

def test_batch_ssi():
    ssi = SSIService()
    if ssi.login():
        print("Logged in")
        urls = [
            f"{ssi.base_url}/Market/SecuritiesDetails",
        ]
        
        params = {
            "lookupRequest.symbol": "VIC,ASP,VCB", # Or "VIC, ASP, VCB"
            "lookupRequest.pageIndex": 1,
            "lookupRequest.pageSize": 50
        }
        res = requests.get(urls[0], headers=ssi._get_headers(), params=params)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print(res.json())
        else:
            print(res.text)
                
    else:
        print("Login failed")

if __name__ == "__main__":
    test_batch_ssi()
