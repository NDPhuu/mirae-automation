import asyncio
import time
from src.services.sync_manager import SyncManager
from src.services.ssi_service import SSIService

async def test_session_expiry_resilience():
    print("🧪 [Test] Bắt đầu test khả năng hồi phục khi Token hết hạn...")
    manager = SyncManager()
    # Giả lập token sai/hết hạn
    manager.ssi.access_token = "EXPIRED_TOKEN_123"
    
    symbols = ["FPT", "VIC"] # Test nhanh
    print(f"🔄 Đang kích hoạt Sync với Token giả...")
    task = await manager.start_eod_sync(symbols)
    
    # Đợi sync chạy xong
    while True:
        status = manager.active_task
        if not status or status["status"] in ["completed", "error"]:
            print(f"🏁 Kết quả Sync: {status['status'] if status else 'None'}")
            break
        print(f"   ... Đang chạy: {status['processed']}/{status['total']}")
        await asyncio.sleep(2)

async def test_concurrent_sync():
    print("\n🧪 [Test] Bắt đầu test 'Join the Train' (Nhiều người bấm cùng lúc)...")
    manager = SyncManager()
    symbols = ["FPT", "VNM", "HPG"]
    
    # Kích hoạt 2 sync cùng lúc
    print("🚀 User A bấm Sync...")
    task_a = await manager.start_eod_sync(symbols)
    
    print("🚀 User B bấm Sync sau 2 giây...")
    await asyncio.sleep(2)
    task_b = await manager.start_eod_sync(symbols)
    
    print(f"📝 Task A ID: {task_a['id']}")
    print(f"📝 Task B ID: {task_b['id']}")
    
    if task_a["id"] == task_b["id"]:
        print("✅ THÀNH CÔNG: User B đã tự động nhập hội (Join) vào Task của User A.")
    else:
        print("❌ THẤT BẠI: Hệ thống tạo 2 task riêng biệt gây xung đột!")

if __name__ == "__main__":
    asyncio.run(test_session_expiry_resilience())
    asyncio.run(test_concurrent_sync())
