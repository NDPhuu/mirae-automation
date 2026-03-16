import os
import sys
sys.path.append(os.getcwd())
from src.services.dnse_service import DNSEService
import json

dnse = DNSEService()
if dnse.login():
    data = dnse.fetch_all_data(["HPG", "VIC", "VNM"])
    if data and "stocks" in data and data["stocks"]:
        first_symbol = list(data["stocks"].keys())[0]
        print(f"Data for {first_symbol}:")
        print(json.dumps(data["stocks"][first_symbol], indent=2))
    else:
        print("Data is null or missing stocks")
else:
    print("Login failed")
