# File: backend/src/services/sync_manager.py
import asyncio
import threading
from datetime import datetime
from typing import List, Dict, Optional
from src.services.ssi_service import SSIService
from src.workers.market_streamer import initial_seed_data
from src.cache import db
from src.cache.state import SYSTEM_STATUS

class SyncManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SyncManager, cls).__new__(cls)
                cls._instance._init_manager()
            return cls._instance

    def _init_manager(self):
        self.active_task = None
        self.ssi = SSIService()
        self.semaphore = asyncio.Semaphore(1)
        # Ngưỡng thời gian chốt EOD (15:10)
        self.EOD_CUTOFF_HOUR = 15
        self.EOD_CUTOFF_MINUTE = 10

    async def start_eod_sync(self, symbols: List[str], force: bool = False):
        """Khởi động luồng đồng bộ. Hỗ trợ phân loại INTRADAY/EOD."""
        now = datetime.now()
        sync_date = now.strftime("%Y-%m-%d")
        task_id = f"sync-{sync_date}"
        
        # Xác định loại task dựa trên thời gian
        is_eod_time = (now.hour > self.EOD_CUTOFF_HOUR) or \
                      (now.hour == self.EOD_CUTOFF_HOUR and now.minute >= self.EOD_CUTOFF_MINUTE)
        task_type = "EOD" if is_eod_time else "INTRADAY"

        # 1. Join the Train / Idempotency
        if self.active_task and self.active_task["id"] == task_id:
            # Nếu đang chạy -> Cho 'lên tàu' xem chung progress
            if self.active_task["status"] == "running":
                return self.active_task
            
            # Nếu đã xong EOD -> Không tải lại trừ khi Force
            if self.active_task["status"] == "completed" and self.active_task["type"] == "EOD" and not force:
                return self.active_task

        # 2. Khởi tạo Task mới
        self.active_task = {
            "id": task_id,
            "date": sync_date,
            "type": task_type,
            "status": "running",
            "total": len(symbols),
            "processed": 0,
            "failed": 0,
            "failed_symbols": [],
            "eta_seconds": len(symbols) * 1.1,
            "started_at": now.isoformat()
        }

        # Chạy ngầm
        asyncio.create_task(self._run_sync_loop(symbols))
        
        return self.active_task

    async def _run_sync_loop(self, symbols: List[str]):
        """Luồng xử lý đồng bộ hợp nhất: DNSE (vài giây) -> SSI (vài phút)"""
        if not self.ssi.access_token:
            self.ssi.login()

        # Bước 1: DNSE Metrics (VNIndex, Top Impact, Prices) - Cập nhật tức thì
        try:
            SYSTEM_STATUS["message"] = "Đang nạp metrics từ DNSE..."
            # Chạy initial_seed_data trong thread riêng vì nó là đồng bộ
            await asyncio.to_thread(initial_seed_data, symbols, force_tier2=True)
            print("✅ [Sync] DNSE metrics updated successfully.")
        except Exception as e:
            print(f"⚠️ [Sync] DNSE fetch error: {e}")

        # Bước 2: SSI Foreign Trading - Chạy vòng lặp có Rate Limit
        for i, sym in enumerate(symbols):
            if self.active_task["status"] != "running":
                break

            async with self.semaphore:
                try:
                    # Make blocking HTTP request inside a thread pool
                    data = await asyncio.to_thread(self.ssi.get_daily_stock_price, sym)
                    if data:
                        # Robust key extraction (Case-insensitive)
                        buy = float(data.get("ForeignBuyValTotal") or data.get("foreignbuyvaltotal") or data.get("f_buy_val") or 0)
                        sell = float(data.get("ForeignSellValTotal") or data.get("foreignsellvaltotal") or data.get("f_sell_val") or 0)
                        # Extract date from SSI response if possible
                        raw_date = data.get("TradingDate") or data.get("tradingdate")
                        iso_date = None
                        if raw_date:
                            try:
                                d, m, y = raw_date.split('/')
                                iso_date = f"{y}-{m}-{d}"
                            except Exception:
                                pass
                        
                        target_date = iso_date if iso_date else task_id.replace("sync-", "")
                        
                        if buy > 0 or sell > 0:
                            # MUST NOT USE immediate=True in an async loop! It will do a synchronous DB flush and block the event loop.
                            # Using immediate=False allows the background flusher thread to batch insert data.
                            db.upsert_stock(sym, {"f_buy_val": buy, "f_sell_val": sell}, trading_date=target_date, immediate=False)
                            print(f"✅ [Sync] {sym}: Buy={buy}, Sell={sell} ({target_date})")
                        else:
                            print(f"ℹ️ [Sync] {sym}: No foreign activity on {target_date}")
                    else:
                        print(f"⚠️ [Sync] {sym}: SSI returned no data")
                except Exception as e:
                    self.active_task["failed"] += 1
                    self.active_task["failed_symbols"].append(sym)
                finally:
                    self.active_task["processed"] += 1
                    # Cập nhật ETA
                    remaining = self.active_task["total"] - self.active_task["processed"]
                    self.active_task["eta_seconds"] = remaining * 1.1
                    
                    # Update global status for UI
                    SYSTEM_STATUS["progress"] = self.active_task["processed"]
                    SYSTEM_STATUS["total"] = self.active_task["total"]
                    SYSTEM_STATUS["message"] = f"Đang đồng bộ {sym} ({self.active_task['processed']}/{self.active_task['total']})"

                # Chờ 1.05s để lách Rate Limit
                await asyncio.sleep(1.05)
                
        # Final flush to guarantee all data is written to DB before marking complete
        await asyncio.to_thread(db.flush_buffers)

        self.active_task["status"] = "completed"
        self.active_task["finished_at"] = datetime.now().isoformat()
        SYSTEM_STATUS["state"] = "READY"
        SYSTEM_STATUS["message"] = "Đồng bộ EOD hoàn tất."

    def get_status(self):
        return self.active_task or {"status": "idle"}

sync_manager = SyncManager()
