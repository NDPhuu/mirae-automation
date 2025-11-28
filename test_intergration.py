# File: test_integration.py
from src.services.dnse_service import DNSEService
from src.services.market_logic import MarketLogic
from src.config import SECTOR_MAPPING

def main():
    print("🚀 BẮT ĐẦU TEST TÍCH HỢP...")
    
    # 1. Chuẩn bị danh sách mã cần lấy (Gộp tất cả mã trong các ngành lại)
    all_symbols = []
    for symbols in SECTOR_MAPPING.values():
        all_symbols.extend(symbols)
    
    # Loại bỏ mã trùng lặp (nếu có)
    all_symbols = list(set(all_symbols))
    print(f"📋 Danh sách theo dõi: {len(all_symbols)} mã.")

    # 2. Gọi Service lấy dữ liệu
    service = DNSEService()
    raw_data = service.fetch_all_data(all_symbols)
    
    if not raw_data or not raw_data["index"]:
        print("❌ Lỗi: Không lấy được dữ liệu.")
        return

    print("\n✅ Đã lấy dữ liệu thô thành công!")
    print(f"   - Index: {raw_data['index'].point}")
    print(f"   - Số mã cổ phiếu lấy được: {len(raw_data['stocks'])}")

    # 3. Gọi Logic phân tích
    logic = MarketLogic()
    report_input = logic.prepare_report_input(raw_data)
    
    print("\n📊 KẾT QUẢ PHÂN TÍCH (LOGIC):")
    print("-" * 30)
    print(f"1. Top Tăng: {report_input.impact_positive}")
    print(f"2. Top Giảm: {report_input.impact_negative}")
    print("-" * 30)
    print("3. Diễn biến Ngành:")
    for sec in report_input.sectors:
        print(f"   > {sec.name}: {sec.avg_change}% ({sec.status})")
        print(f"     - Mã tiêu biểu: {', '.join(sec.top_gainers)}")

if __name__ == "__main__":
    main()