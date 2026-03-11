import sys
import os
import time
from typing import Dict, Any

# Ensure we can import src module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.ssi_service import SSIService
from src.services.dnse_service import DNSEService
from src.services.market_data_aggregator import MarketDataAggregator
from src.services.market_logic import MarketLogic
from src.models import StockData, MarketIndex

symbols = ["VCB", "CTG", "MBB", "VIC", "GAS", "BSR", "HPG", "MWG", "FPT", "STB", "VPB"]

def run_validation():
    print("====================================")
    print("1. API SCHEMA VALIDATION")
    print("====================================")
    
    dnse = DNSEService()
    ssi = SSIService()
    
    dnse_login = dnse.login()
    ssi_login = ssi.login()
    print(f"DNSE login: {dnse_login}, SSI login: {ssi_login}")
    
    print("\nFetching DNSE payload...")
    dnse_data = dnse.fetch_all_data(symbols)
    dnse_stocks = dnse_data.get("stocks", {}) if dnse_data else {}
    dnse_index = dnse_data.get("index") if dnse_data else None
    
    print("\nFetching SSI payload...")
    ssi_foreign = ssi.get_batch_foreign_data(symbols)
    ssi_listed = ssi.get_securities_details(symbols)
    
    print("\n--- SCHEMA VERIFICATION (Example VCB) ---")
    if "VCB" in dnse_stocks:
        print(f"DNSE VCB Fields: {list(dnse_stocks['VCB'].keys())}")
    if "VCB" in ssi_foreign:
        print(f"SSI VCB Foreign Fields: {list(ssi_foreign['VCB'].keys())}")
    if "VCB" in ssi_listed:
        print(f"SSI VCB shares: {ssi_listed['VCB']}")
        
    print("\n====================================")
    print("2. DATA CONSISTENCY CHECK (SSI vs DNSE)")
    print("====================================")
    
    for sym in symbols:
        d_stock = dnse_stocks.get(sym, {})
        d_price = d_stock.get("price")
        d_f_buy = d_stock.get("f_buy_val", 0)
        d_f_sell = d_stock.get("f_sell_val", 0)
        d_shares = d_stock.get("listed_shares", 0)
        
        s_f_buy = ssi_foreign.get(sym, {}).get("f_buy_val", 0)
        s_f_sell = ssi_foreign.get(sym, {}).get("f_sell_val", 0)
        s_shares = ssi_listed.get(sym, 0)
        
        print(f"\n[{sym}]")
        print(f"  Price DNSE: {d_price}")
        print(f"  Shares -> DNSE: {d_shares} | SSI: {s_shares}")
        print(f"  F.Buy  -> DNSE: {d_f_buy} (Billion?) | SSI: {s_f_buy} (Raw VND)")
        print(f"  F.Sell -> DNSE: {d_f_sell} (Billion?) | SSI: {s_f_sell} (Raw VND)")
        
    print("\n====================================")
    print("3. RECALCULATED IMPACT RESULTS & RANKING")
    print("====================================")
    
    # We will build unified models manually for verification matching our logic
    stocks_dict = {}
    market_caps = {}
    
    for sym in symbols:
        d_stock = dnse_stocks.get(sym, {})
        stocks_dict[sym] = StockData(
            symbol=sym,
            price=d_stock.get("price", 0) or 0.0,
            ref_price=d_stock.get("ref_price", 0) or 0.0,
            change_percent=d_stock.get("change_percent", 0) or 0.0,
            shares=ssi_listed.get(sym, 0),        # SSI static
            volume=int(d_stock.get("volume", 0) or 0),
            f_buy_val=float(d_stock.get("f_buy_val", 0) or 0.0) * 1_000_000_000, 
            f_sell_val=float(d_stock.get("f_sell_val", 0) or 0.0) * 1_000_000_000
        )
        # 1. Market Cap
        price = stocks_dict[sym].price
        shares = stocks_dict[sym].shares
        market_caps[sym] = price * shares
        
    # We will compute the manual impact points:
    # Notice we need a proxy for "total_market_cap" because our subset of shares
    # generates a tiny total_market_cap compared to the whole index.
    # To correctly calculate impact, total_market_cap must represent the WHOLE index.
    
    # We will check if the market_logic uses local proxy or we can emulate a global total_market_cap.
    # As the user notes, VNINDEX total_market_cap is approx 7.87e15 (7,870,000,000,000,000)
    GIVEN_TOTAL_MKTCAP = 7.87e15
    VNINDEX_LEVEL = dnse_index.point if dnse_index else 1676.0
    
    print(f"Using Global Estimated Total Market Cap: {GIVEN_TOTAL_MKTCAP}")
    print(f"Using VNINDEX Level: {VNINDEX_LEVEL}\n")
    
    manual_results = []
    
    for sym, stock in stocks_dict.items():
        mcap = market_caps[sym]
        weight = mcap / GIVEN_TOTAL_MKTCAP if GIVEN_TOTAL_MKTCAP > 0 else 0
        
        prc = stock.price
        ref = stock.ref_price
        pct_change = (prc - ref) / ref if ref > 0 else 0
        
        pct_impact = weight * pct_change
        impact_pts = VNINDEX_LEVEL * pct_impact
        
        manual_results.append({
            "symbol": sym, 
            "mcap": mcap,
            "weight": weight,
            "pct_change": pct_change,
            "pct_impact": pct_impact,
            "impact_pts": impact_pts,
            "ds_change": stock.change_percent
        })
        
    manual_results.sort(key=lambda x: x["impact_pts"], reverse=True)
    
    for r in manual_results:
        print(f"{r['symbol']:4} | W: {r['weight']*100:6.3f}% | Chg: {r['pct_change']*100:6.2f}% | Pts: {r['impact_pts']:+5.2f} (Sys UI: {r['ds_change']:+.2f}%)")

if __name__ == "__main__":
    run_validation()
