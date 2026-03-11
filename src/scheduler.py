from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import text
from src.database import engine
from src.workers.market_streamer import initial_seed_data
from src.config import SECTOR_MAPPING

def poll_market_data():
    all_symbols = []
    for symbols in SECTOR_MAPPING.values():
        all_symbols.extend(symbols)
    all_symbols = list(set(all_symbols))
    
    print("🔄 [Scheduler] Chạy cron job: Lấy dữ liệu DNSE/SSI...")
    initial_seed_data(all_symbols)

def cleanup_old_data():
    if not engine:
        print("❌ [Scheduler] Không có kết nối Database để dọn rác!")
        return

    print("🧹 [Scheduler] Chạy cron job: Dọn dẹp dữ liệu cũ (Quá 30 ngày)...")
    with engine.begin() as conn:
        cleanup_queries = [
            "DELETE FROM market_prices WHERE trading_date < CURRENT_DATE - 30",
            "DELETE FROM foreign_trading WHERE trading_date < CURRENT_DATE - 30",
            "DELETE FROM index_snapshot WHERE trading_date < CURRENT_DATE - 30"
        ]
        total_deleted = 0
        for q in cleanup_queries:
            res = conn.execute(text(q))
            total_deleted += res.rowcount
            
        print(f"✅ [Scheduler] Đã xóa {total_deleted} bản ghi cũ.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # 1. Job Ingestion: Mỗi 1 phút trong giờ hành chính (T2-T6, 9h-15h)
    scheduler.add_job(
        poll_market_data,
        CronTrigger(day_of_week='mon-fri', hour='9-15', minute='*'),
        id='poll_market_data_job',
        replace_existing=True
    )
    
    # 2. Job Cleanup: 23:00 hằng ngày
    scheduler.add_job(
        cleanup_old_data,
        CronTrigger(hour='23', minute='0'),
        id='cleanup_old_data_job',
        replace_existing=True
    )
    
    scheduler.start()
    print("⏳ [Scheduler] APScheduler đã khởi động (Ingestion: 1 phút/lần 9-15h, Cleanup: 23h).")
    return scheduler
