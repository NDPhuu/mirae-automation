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

import os
import pandas as pd
import boto3
from datetime import datetime, timedelta
from io import BytesIO

def get_r2_client():
    return boto3.client(
        service_name='s3',
        endpoint_url=os.getenv("R2_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
        region_name="auto"
    )

def cleanup_old_data():
    if not engine:
        print("❌ [Scheduler] Không có kết nối Database để dọn rác!")
        return

    print("🧹 [Scheduler] Bắt đầu quá trình lưu trữ R2 và dọn dẹp dữ liệu cũ (Quá 30 ngày)...")
    bucket_name = os.getenv("R2_BUCKET_NAME", "mirae-archive")
    thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
    
    tables = ["market_prices", "foreign_trading", "index_snapshot"]
    total_deleted = 0
    
    try:
        # Tùy chọn: dùng AWS/S3 API nếu không có R2_ENDPOINT_URL
        s3 = get_r2_client() if os.getenv("R2_ENDPOINT_URL") else None
        
        for table in tables:
            query = f"SELECT * FROM {table} WHERE trading_date < '{thirty_days_ago.isoformat()}'"
            df = pd.read_sql_query(query, engine)
            
            if not df.empty:
                if s3:
                    # Convert date column to string for parquet compatibility
                    df['trading_date'] = df['trading_date'].astype(str)
                    
                    # Save to parquet in memory
                    out_buffer = BytesIO()
                    df.to_parquet(out_buffer, index=False)
                    out_buffer.seek(0)
                    
                    # Upload to R2
                    object_key = f"archive/{table}/{table}_{thirty_days_ago.isoformat()}_{int(datetime.now().timestamp())}.parquet"
                    s3.upload_fileobj(out_buffer, bucket_name, object_key)
                    print(f"📦 [Archive] Đã upload {len(df)} dòng của {table} lên R2 ({object_key})")
                else:
                    print(f"⚠️ [Archive] R2 credentials missing. Skipping cloud backup for {table}.")

                # After successful upload (or skip), delete from database
                with engine.begin() as conn:
                    delete_q = f"DELETE FROM {table} WHERE trading_date < '{thirty_days_ago.isoformat()}'"
                    res = conn.execute(text(delete_q))
                    total_deleted += res.rowcount
            else:
                print(f"📦 [Archive] {table}: Không có dữ liệu cũ cần dọn.")
                
        print(f"✅ [Scheduler] Đã hoàn tất, tổng xóa {total_deleted} bản ghi cũ.")
    except Exception as e:
        print(f"❌ [Scheduler] Lỗi trong quá trình Archive/Delete: {e}")

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
