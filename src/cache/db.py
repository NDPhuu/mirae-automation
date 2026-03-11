import sqlite3
import os
from typing import List, Dict, Tuple
from datetime import datetime

# Define DB path in the same directory as this file
DB_PATH = os.path.join(os.path.dirname(__file__), 'market_cache.sqlite')

def get_connection():
    """Returns a threaded SQLite connection with WAL mode enabled for concurrency."""
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    # WAL mode allows simultaneous readers and writers (great for our Streamlit UI reading while worker writes)
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def init_db():
    """Initializes the SQLite database tables if they don't exist."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Table for Market Index (e.g. VNINDEX)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_index (
                symbol TEXT PRIMARY KEY,
                point REAL,
                change_point REAL,
                change_percent REAL,
                total_volume REAL,
                total_value REAL,
                breadth_green INTEGER,
                breadth_red INTEGER,
                breadth_yellow INTEGER,
                breadth_ceiling INTEGER,
                breadth_floor INTEGER,
                updated_at TEXT
            )
        ''')
        
        # Table for Individual Stocks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT PRIMARY KEY,
                price REAL,
                ref_price REAL,
                change_percent REAL,
                shares INTEGER,
                volume INTEGER,
                f_buy_val REAL,
                f_sell_val REAL,
                updated_at TEXT
            )
        ''')
        
        conn.commit()
    finally:
        conn.close()

def upsert_index(symbol: str, data: dict):
    conn = get_connection()
    try:
        conn.execute('''
            INSERT INTO market_index (
                symbol, point, change_point, change_percent, total_volume, total_value,
                breadth_green, breadth_red, breadth_yellow, breadth_ceiling, breadth_floor, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                point=excluded.point,
                change_point=excluded.change_point,
                change_percent=excluded.change_percent,
                total_volume=excluded.total_volume,
                total_value=excluded.total_value,
                breadth_green=excluded.breadth_green,
                breadth_red=excluded.breadth_red,
                breadth_yellow=excluded.breadth_yellow,
                breadth_ceiling=excluded.breadth_ceiling,
                breadth_floor=excluded.breadth_floor,
                updated_at=excluded.updated_at
        ''', (
            symbol, data.get('point', 0.0), data.get('change_point', 0.0), data.get('change_percent', 0.0),
            data.get('total_volume', 0.0), data.get('total_value', 0.0),
            data.get('breadth_green', 0), data.get('breadth_red', 0), data.get('breadth_yellow', 0),
            data.get('breadth_ceiling', 0), data.get('breadth_floor', 0),
            datetime.now().isoformat()
        ))
        conn.commit()
    finally:
        conn.close()

def upsert_stock(symbol: str, data: dict):
    conn = get_connection()
    try:
        # We only update the fields that are provided in the dict.
        # This is useful because DNSE updates price/volume, while SSI updates f_buy/f_sell independently.
        current_time = datetime.now().isoformat()
        
        # Build dynamic queries based on what's available
        fields = ["symbol", "updated_at"]
        values = [symbol, current_time]
        
        for k in ["price", "ref_price", "change_percent", "shares", "volume", "f_buy_val", "f_sell_val"]:
            if k in data:
                fields.append(k)
                values.append(data[k])
                
        placeholders = ", ".join(["?"] * len(fields))
        columns = ", ".join(fields)
        updates = ", ".join([f"{f}=excluded.{f}" for f in fields if f != "symbol"])
        
        query = f'''
            INSERT INTO stocks ({columns}) VALUES ({placeholders})
            ON CONFLICT(symbol) DO UPDATE SET {updates}
        '''
        conn.execute(query, tuple(values))
        conn.commit()
    finally:
        conn.close()

def get_market_index(symbol: str = "VNINDEX") -> dict:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM market_index WHERE symbol=?", (symbol,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_stocks(symbols: List[str]) -> Dict[str, dict]:
    if not symbols:
        return {}
    conn = get_connection()
    try:
        placeholders = ",".join(["?"] * len(symbols))
        rows = conn.execute(f"SELECT * FROM stocks WHERE symbol IN ({placeholders})", tuple(symbols)).fetchall()
        return {row['symbol']: dict(row) for row in rows}
    finally:
        conn.close()

# Initialize upon import automatically
init_db()
