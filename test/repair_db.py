import json
import os
import sys

# Add root dir to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.cache import db

def repair():
    print("--- REPAIR TOOL: JSON to SQLITE SYNC ---")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(root_dir, "data", "listed_shares_cache.json")
    
    if not os.path.exists(cache_path):
        print(f"❌ ERROR: File not found at {cache_path}")
        return

    try:
        with open(cache_path, "r", encoding='utf-8') as f:
            cache_data = json.load(f)
            shares_map = cache_data.get("shares", {})
            print(f"Found {len(shares_map)} shares in JSON.")
            
            count = 0
            for sym, shares in shares_map.items():
                if shares > 0:
                    db.upsert_stock(sym, {"shares": shares})
                    count += 1
            
            print(f"✅ SUCCESSFULLY REPAIRED: {count} symbols updated in SQLite.")
    except Exception as e:
        print(f"❌ ERROR reading JSON: {e}")

if __name__ == "__main__":
    repair()
