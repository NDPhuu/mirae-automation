import os
import json
import logging
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.services.ssi_service import SSIService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MOCK_CACHE_FILE = os.path.join(os.path.dirname(__file__), "data", "mock_listed_shares_cache.json")

def test_fallback_logic():
    """
    Test script that only fetches 3 symbols (2 real, 1 totally fake)
    to prove out the 5-Phase Fallback logic without taking 10 minutes.
    """
    logger.info("Starting MOCK SSI Cache Update...")
    
    # 1. Phase 1: Small Batch Fetch
    test_symbols = ["VIC", "VCB", "FAKE123", "MISSING_CORP"]
    logger.info(f"Targeting mock symbols: {test_symbols}")
    
    ssi = SSIService()
    if not ssi.login():
        logger.error("Failed to login to SSI.")
        return
        
    logger.info("Phase 1: Fetching initial batch from SSI...")
    # NOTE: The real Service will drop FAKE123 because it returns nothing.
    listed_shares = ssi.get_securities_details(test_symbols)
    
    # 2. Phase 2: Identify Missing
    for sym in test_symbols:
        if sym not in listed_shares:
            listed_shares[sym] = 0
            
    missing_symbols = [sym for sym, shares in listed_shares.items() if shares == 0]
    
    # 3. Phase 3: Auto-Retry (Slow)
    if missing_symbols:
        logger.warning(f"Phase 2: Identified {len(missing_symbols)} missing symbols: {missing_symbols}")
        logger.info("Phase 3: Attempting slow auto-retry (2-second interval) for missing symbols...")
        
        for sym in missing_symbols:
            logger.info(f"Retrying -> {sym}")
            retry_result = ssi.get_securities_details([sym])
            
            if sym in retry_result and retry_result[sym] > 0:
                logger.info(f"✅ Recovered {sym} = {retry_result[sym]} shares!")
                listed_shares[sym] = retry_result[sym]
            else:
                logger.error(f"❌ Retry failed for {sym}.")
            
            time.sleep(2.0)
            
    # 4. Phase 4: Human-in-the-Loop CLI Fallback
    final_missing = [sym for sym, shares in listed_shares.items() if shares == 0]
    
    if final_missing:
         logger.warning(f"Phase 4 (CRITICAL): {len(final_missing)} symbols severely missing data.")
         print("\n" + "="*50)
         print("   ⚠️  MANUAL OVERRIDE REQUIRED  ⚠️")
         print("="*50)
         print("The following symbols returned 0 from the API.")
         print("Please input the listed shares (e.g. from Vietstock).")
         print("Press [ENTER] to skip and leave as 0.\n")
         
         for sym in final_missing:
             while True:
                user_input = input(f"Enter Listed Shares for [{sym}]: ").strip()
                if not user_input:
                    logger.info(f"Skipped {sym}. Leaving as 0.")
                    break
                try:
                    human_shares = int(user_input.replace(",", "")) # Convert string 5,000,000 -> 5000000
                    listed_shares[sym] = human_shares
                    logger.info(f"✅ Human override accepted: {sym} = {human_shares}")
                    break
                except ValueError:
                    print("❌ Invalid input! Please type an integer (e.g., 500000000) or press Enter to skip.")
                    
    # 5. Phase 5: Save
    try:
        os.makedirs(os.path.dirname(MOCK_CACHE_FILE), exist_ok=True)
        from datetime import datetime
        with open(MOCK_CACHE_FILE, "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "shares": listed_shares
            }, f, indent=4)
        logger.info(f"Phase 5: Successfully saved MOCK cache to {MOCK_CACHE_FILE}.")
    except Exception as e:
        logger.error(f"Error saving cache: {e}")

if __name__ == "__main__":
    test_fallback_logic()
