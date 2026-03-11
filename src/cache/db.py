import threading
import time
from datetime import datetime, date
from sqlalchemy import text
from src.database import engine
from typing import List, Dict

_index_buffer = {}
_stock_buffer = {}
_buffer_lock = threading.Lock()
_flusher_thread = None
_stop_event = threading.Event()

def start_flusher():
    global _flusher_thread
    if _flusher_thread is None or not _flusher_thread.is_alive():
        _stop_event.clear()
        _flusher_thread = threading.Thread(target=_flush_loop, daemon=True)
        _flusher_thread.start()
        print("🚀 [DB Cache] Background UPSERT flusher started.")

def stop_flusher():
    _stop_event.set()
    if _flusher_thread:
        _flusher_thread.join(timeout=2.0)
    flush_buffers() # Final flush

def _flush_loop():
    while not _stop_event.is_set():
        time.sleep(2.0) # Flush every 2 seconds
        flush_buffers()

def upsert_index(symbol: str, data: dict):
    with _buffer_lock:
        if symbol not in _index_buffer:
            _index_buffer[symbol] = {}
        _index_buffer[symbol].update(data)

def upsert_stock(symbol: str, data: dict, trading_date: str = None):
    with _buffer_lock:
        if symbol not in _stock_buffer:
            _stock_buffer[symbol] = {}
        if trading_date:
            data["_explicit_date"] = trading_date
        _stock_buffer[symbol].update(data)

def flush_buffers():
    if not engine:
        return
        
    with _buffer_lock:
        if not _index_buffer and not _stock_buffer:
            return
        
        indexes_to_flush = _index_buffer.copy()
        stocks_to_flush = _stock_buffer.copy()
        
        _index_buffer.clear()
        _stock_buffer.clear()
        
    current_date = date.today().isoformat()
    updated_at = datetime.now()
    
    try:
        with engine.begin() as conn:
            # 1. Flush Index Snapshot
            if indexes_to_flush:
                idx_params = []
                for sym, data in indexes_to_flush.items():
                    idx_params.append({
                        "symbol": sym,
                        "trading_date": current_date,
                        "point": data.get('point'),
                        "change_point": data.get('change_point'),
                        "change_percent": data.get('change_percent'),
                        "total_volume": data.get('total_volume'),
                        "total_value": data.get('total_value'),
                        "breadth_green": data.get('breadth_green'),
                        "breadth_red": data.get('breadth_red'),
                        "breadth_yellow": data.get('breadth_yellow'),
                        "breadth_ceiling": data.get('breadth_ceiling'),
                        "breadth_floor": data.get('breadth_floor'),
                        "updated_at": updated_at
                    })
                
                idx_query = text("""
                    INSERT INTO index_snapshot (
                        symbol, trading_date, point, change_point, change_percent, total_volume, total_value,
                        breadth_green, breadth_red, breadth_yellow, breadth_ceiling, breadth_floor, updated_at
                    ) VALUES (
                        :symbol, :trading_date, :point, :change_point, :change_percent, :total_volume, :total_value,
                        :breadth_green, :breadth_red, :breadth_yellow, :breadth_ceiling, :breadth_floor, :updated_at
                    )
                    ON CONFLICT (symbol, trading_date) DO UPDATE SET
                        point=COALESCE(EXCLUDED.point, index_snapshot.point),
                        change_point=COALESCE(EXCLUDED.change_point, index_snapshot.change_point),
                        change_percent=COALESCE(EXCLUDED.change_percent, index_snapshot.change_percent),
                        total_volume=COALESCE(EXCLUDED.total_volume, index_snapshot.total_volume),
                        total_value=COALESCE(EXCLUDED.total_value, index_snapshot.total_value),
                        breadth_green=COALESCE(EXCLUDED.breadth_green, index_snapshot.breadth_green),
                        breadth_red=COALESCE(EXCLUDED.breadth_red, index_snapshot.breadth_red),
                        breadth_yellow=COALESCE(EXCLUDED.breadth_yellow, index_snapshot.breadth_yellow),
                        breadth_ceiling=COALESCE(EXCLUDED.breadth_ceiling, index_snapshot.breadth_ceiling),
                        breadth_floor=COALESCE(EXCLUDED.breadth_floor, index_snapshot.breadth_floor),
                        updated_at=EXCLUDED.updated_at
                """)
                conn.execute(idx_query, idx_params)

            # 2. Flush Stocks Data
            if stocks_to_flush:
                st_params = []
                mp_params = []
                ft_params = []
                
                for sym, data in stocks_to_flush.items():
                    # Handle explicit date if provided (e.g. for SSI EOD data)
                    explicit_date = data.pop("_explicit_date", None)
                    target_date = explicit_date if explicit_date else current_date
                    
                    # Listed Shares / Sector
                    if "shares" in data or "sector" in data:
                        st_params.append({
                            "symbol": sym,
                            "shares": data.get("shares"),
                            "sector": data.get("sector")
                        })
                        
                    # Market Prices
                    if any(k in data for k in ["price", "ref_price", "change_percent", "volume"]):
                        mp_params.append({
                            "symbol": sym,
                            "trading_date": target_date,
                            "price": data.get("price"),
                            "ref_price": data.get("ref_price"),
                            "volume": data.get("volume"),
                            "updated_at": updated_at
                        })
                        
                    # Foreign Trading
                    if any(k in data for k in ["f_buy_val", "f_sell_val"]):
                        ft_params.append({
                            "symbol": sym,
                            "trading_date": target_date,
                            "f_buy_val": data.get("f_buy_val"),
                            "f_sell_val": data.get("f_sell_val"),
                            "updated_at": updated_at
                        })
                
                if st_params:
                    # Use a robust UPSERT that handles potential NULLs in the GREATEST comparison
                    # and ensuring we have correct parameter binding names
                    st_query = text("""
                        INSERT INTO stocks (symbol, listed_shares, sector) 
                        VALUES (:symbol, :shares, :sector)
                        ON CONFLICT (symbol) DO UPDATE SET
                            listed_shares = GREATEST(COALESCE(stocks.listed_shares, 0), COALESCE(EXCLUDED.listed_shares, 0)),
                            sector = COALESCE(EXCLUDED.sector, stocks.sector)
                    """)
                    conn.execute(st_query, st_params)
                    
                if mp_params:
                    mp_query = text("""
                        INSERT INTO market_prices (symbol, trading_date, price, ref_price, volume, updated_at)
                        VALUES (:symbol, :trading_date, :price, :ref_price, :volume, :updated_at)
                        ON CONFLICT (symbol, trading_date) DO UPDATE SET
                            price=COALESCE(EXCLUDED.price, market_prices.price),
                            ref_price=COALESCE(EXCLUDED.ref_price, market_prices.ref_price),
                            volume=COALESCE(EXCLUDED.volume, market_prices.volume),
                            updated_at=EXCLUDED.updated_at
                    """)
                    conn.execute(mp_query, mp_params)
                    
                if ft_params:
                    ft_query = text("""
                        INSERT INTO foreign_trading (symbol, trading_date, f_buy_val, f_sell_val, updated_at)
                        VALUES (:symbol, :trading_date, :f_buy_val, :f_sell_val, :updated_at)
                        ON CONFLICT (symbol, trading_date) DO UPDATE SET
                            f_buy_val=COALESCE(EXCLUDED.f_buy_val, foreign_trading.f_buy_val),
                            f_sell_val=COALESCE(EXCLUDED.f_sell_val, foreign_trading.f_sell_val),
                            updated_at=EXCLUDED.updated_at
                    """)
                    conn.execute(ft_query, ft_params)
    except Exception as e:
        print(f"⚠️ [DB Cache] Error flushing to DB: {e}")

def init_db():
    start_flusher()
