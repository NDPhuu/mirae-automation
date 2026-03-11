import os
import sys

# Thêm root dir vào sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(root_dir)

from src.services.data_aggregator import DataAggregator
from src.config import SECTOR_MAPPING
import time

def test_cache_speed():
    all_symbols = []
    for symbols in SECTOR_MAPPING.values():
        all_symbols.extend(symbols)
    all_symbols = list(set(all_symbols))

    print(f"Bắt đầu lấy dữ liệu {len(all_symbols)} mã từ CACHE SQLite...")
    
    start_time = time.time()
    
    aggregator = DataAggregator()
    index_data, stocks_dict = aggregator.fetch_market_data(all_symbols)
    
    end_time = time.time()
    
    if not index_data:
        print("❌ LỖI: Cache trống. Bạn đã chạy 'python src/workers/market_streamer.py' ở một terminal khác chưa?")
        return
        
    print(f"✅ Hoàn thành trong {end_time - start_time:.4f} giây!")
    print(f"📊 VNINDEX: {index_data.point} ({index_data.change_point})")
    print(f"📈 Tăng: {index_data.breadth.green} | Giảm: {index_data.breadth.red} | Trần: {index_data.breadth.ceiling} | Sàn: {index_data.breadth.floor}")
    
    # Check HPG if exists
    if "HPG" in stocks_dict:
        hpg = stocks_dict["HPG"]
        print(f"🏭 HPG - Giá: {hpg.price} | NN Mua: {hpg.f_buy_val} | NN Bán: {hpg.f_sell_val}")
    else:
        print("💡 HPG chưa có trong cache.")

if __name__ == "__main__":
    test_cache_speed()
