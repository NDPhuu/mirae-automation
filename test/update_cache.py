import os
import json
import logging
import sys
from datetime import datetime

# Ensure we can import src module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.ssi_service import SSIService
from src.config import SECTOR_MAPPING

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

CACHE_FILE = os.path.join(os.path.dirname(__file__), "data", "listed_shares_cache.json")

def update_cache():
    """
    Script to be run at the start of the day/week to fetch the absolute 
    listed_shares from SSI for all tracked symbols.
    """
    logger.info("Starting SSI Cache Update...")
    
    # Collect all tracked symbols from SECTOR_MAPPING
    symbols = []
    for sector, syms in SECTOR_MAPPING.items():
        symbols.extend(syms)
        
    # Remove duplicates
    symbols = list(set(symbols))
    logger.info(f"Collected {len(symbols)} unique symbols to track.")
    
    ssi = SSIService()
    if not ssi.login():
        logger.error("Failed to login to SSI.")
        return
        
    logger.info("Logged into SSI successfully. Fetching securities details in batch...")
    
    # Actually getting the batch is O(N) unfortunately in the current ssi_service.py 
    # but since this runs once a day via script, it's safer.
    listed_shares = ssi.get_securities_details(symbols)
    
    # Ensure missing symbols are set to 0.
    for sym in symbols:
        if sym not in listed_shares:
            logger.warning(f"Could not fetch listed_shares for {sym}. Setting to 0.")
            listed_shares[sym] = 0
            
    # Save to JSON
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "shares": listed_shares
            }, f, indent=4)
        logger.info(f"Successfully saved cache for {len(listed_shares)} symbols to {CACHE_FILE}.")
    except Exception as e:
        logger.error(f"Error saving cache: {e}")

if __name__ == "__main__":
    update_cache()
