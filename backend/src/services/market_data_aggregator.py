import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Any

from src.services.dnse_service import DNSEService
from src.services.ssi_service import SSIService

logger = logging.getLogger(__name__)

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "listed_shares_cache.json")

class MarketDataAggregator:
    def __init__(self):
        self.dnse = DNSEService()
        self.ssi = SSIService()
        self.listed_shares_cache: Dict[str, int] = {}
        self._load_cache()

    def _load_cache(self):
        """Load listed shares from local cache to avoid repeated SSI calls."""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    data = json.load(f)
                    self.listed_shares_cache = data.get("shares", {})
                    # We can add TTL check here based on 'last_updated' if needed.
            except Exception as e:
                logger.error(f"Error loading cache: {e}")

    def _save_cache(self):
        """Save listed shares to local cache."""
        try:
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            with open(CACHE_FILE, "w") as f:
                json.dump({
                    "last_updated": datetime.now().isoformat(),
                    "shares": self.listed_shares_cache
                }, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def _ensure_ssi_cache(self, symbols: List[str]):
        """Ensure all requested symbols have listedShares cached."""
        missing = [sym for sym in symbols if sym not in self.listed_shares_cache]
        if missing:
            logger.info(f"Fetching listed shares from SSI for {len(missing)} missing symbols...")
            if self.ssi.login():
                new_shares = self.ssi.get_securities_details(missing)
                self.listed_shares_cache.update(new_shares)
                
                # Ensure we don't re-fetch even if SSI doesn't return data for them
                for sym in missing:
                    if sym not in self.listed_shares_cache:
                        self.listed_shares_cache[sym] = 0
                
                self._save_cache()
            else:
                logger.error("SSI Login failed while attempting to cache listed shares.")

    def fetch_unified_market_data(self, symbols: List[str], manual_overrides: Dict[str, dict] = None) -> Tuple[Any, Dict[str, dict]]:
        """
        Coordinates DNSE and SSI to build a unified market data object.
        Implements 3-Layer Architecture:
        1. SSI EOD (Primary for Foreign)
        2. DNSE Real-time (Fallback for Foreign + Primary for Price/Vol)
        3. Manual Overrides (Absolute UI override)
        """
        if manual_overrides is None:
            manual_overrides = {}

        # 1. Merge static data from SSI (cache check)
        self._ensure_ssi_cache(symbols)
        
        # Fetch SSI Foreign Data (Priority 1)
        ssi_foreign = {}
        if self.ssi.login():
            ssi_foreign = self.ssi.get_batch_foreign_data(symbols)
            
        # 2. Fetch real-time DNSE data (Priority 2)
        dnse_data = self.dnse.fetch_all_data(symbols)
        index_data = dnse_data.get("index") if dnse_data else None
        raw_stocks = dnse_data.get("stocks", {}) if dnse_data else {}
        
        # 3. Produce a unified market data object
        unified_stocks = {}
        for sym in symbols:
            # Check manual overrides first
            override = manual_overrides.get(sym, {})
            
            # DNSE Base
            raw_dnse = raw_stocks.get(sym, {})
            
            # Normalization
            # - volume to integer
            if "volume" in override:
                volume = override["volume"]
            else:
                vol_str = raw_dnse.get("volume", "0")
                try:
                    volume = int(float(vol_str)) if vol_str else 0
                except ValueError:
                    volume = 0
                
            # Fallback Logic for Foreign Trading
            # Prioritize Manual -> SSI -> DNSE -> 0
            ssi_f = ssi_foreign.get(sym, {})
            
            # Buy Fallback
            if "foreign_buy" in override:
                f_buy_val = override["foreign_buy"]
            elif ssi_f and ssi_f.get("f_buy_val", 0) > 0:
                f_buy_val = float(ssi_f.get("f_buy_val", 0)) # Raw VND
            else:
                dnse_val = float(raw_dnse.get("f_buy_val") or 0.0)
                f_buy_val = dnse_val * 1_000_000_000 # Convert Billion to Raw VND
                
            # Sell Fallback
            if "foreign_sell" in override:
                f_sell_val = override["foreign_sell"]
            elif ssi_f and ssi_f.get("f_sell_val", 0) > 0:
                f_sell_val = float(ssi_f.get("f_sell_val", 0)) # Raw VND
            else:
                dnse_val = float(raw_dnse.get("f_sell_val") or 0.0)
                f_sell_val = dnse_val * 1_000_000_000 # Convert Billion to Raw VND
            
            # Check manual overrides for price as well, although less common
            price = float(override.get("price", raw_dnse.get("price") or 0.0))
            ref_price = float(override.get("ref_price", raw_dnse.get("ref_price") or 0.0))
            
            # Change Percent
            change_percent = float(override.get("change_percent", raw_dnse.get("change_percent") or 0.0))
            if change_percent == 0.0 and ref_price > 0 and price > 0: # recalc if override changed price
                 change_percent = (price - ref_price) / ref_price * 100
                 
            # Merge with SSI static data
            listed_shares = self.listed_shares_cache.get(sym, 0)
            
            unified_stocks[sym] = {
                "symbol": sym,
                "price": price,
                "ref_price": ref_price,
                "change_percent": change_percent,
                "volume": volume,
                "foreign_buy": f_buy_val,
                "foreign_sell": f_sell_val,
                "listed_shares": listed_shares,
                "timestamp": datetime.now().isoformat()
            }
            
        return index_data, unified_stocks
