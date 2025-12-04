# File: src/services/market_logic.py
from typing import List, Dict
from src.models import StockData, SectorPerformance, DailyReportInput, ForeignTrading
from src.config import SECTOR_MAPPING

class MarketLogic:
    def __init__(self):
        pass

    def analyze_sectors(self, stock_data_dict: Dict[str, dict]) -> List[SectorPerformance]:
        """
        Tính toán hiệu suất từng nhóm ngành dựa trên giá các mã thành phần.
        """
        results = []
        
        for sector_name, symbols in SECTOR_MAPPING.items():
            # Lấy dữ liệu các mã thuộc ngành này
            sector_stocks = []
            total_change = 0.0
            count = 0
            
            for sym in symbols:
                data = stock_data_dict.get(sym)
                if data:
                    # --- FIX: Xử lý an toàn cho change_percent ---
                    raw_change = data.get("change_percent")
                    change = float(raw_change) if raw_change is not None else 0.0
                    # ---------------------------------------------
                    
                    sector_stocks.append({"symbol": sym, "change": change})
                    total_change += change
                    count += 1
            
            if count == 0:
                continue

            # 1. Tính % tăng giảm trung bình của ngành
            avg_change = total_change / count
            
            # 2. Tìm mã Tăng mạnh nhất & Giảm mạnh nhất trong ngành
            # Sắp xếp theo % giảm dần
            sorted_stocks = sorted(sector_stocks, key=lambda x: x["change"], reverse=True)
            
            top_gainers = [s["symbol"] for s in sorted_stocks if s["change"] > 0][:3]
            top_losers = [s["symbol"] for s in sorted_stocks if s["change"] < 0][-3:] # Lấy 3 mã cuối
            
            # 3. Đánh giá trạng thái ngành
            status = "Trung tính"
            if avg_change >= 1.0: status = "Tích cực"
            elif avg_change <= -1.0: status = "Tiêu cực"
            elif avg_change > 0: status = "Khả quan"
            else: status = "Điều chỉnh nhẹ"

            results.append(SectorPerformance(
                name=sector_name,
                avg_change=round(avg_change, 2),
                top_gainers=top_gainers,
                top_losers=top_losers,
                status=status
            ))
            
        # Sắp xếp các ngành: Ngành tăng mạnh nhất lên đầu
        return sorted(results, key=lambda x: x.avg_change, reverse=True)

    def get_top_impact(self, stock_data_dict: Dict[str, dict]) -> (List[str], List[str]):
        """
        Tìm Top mã tác động.
        FIX: Sử dụng trọng số (Giá trị giao dịch * % Thay đổi) để ưu tiên Bluechip.
        Đã thêm cơ chế xử lý lỗi NoneType.
        """
        all_stocks = []
        for sym, data in stock_data_dict.items():
            # --- ĐOẠN CODE FIX LỖI ---
            # Lấy dữ liệu thô
            raw_change = data.get("change_percent")
            raw_price = data.get("price")
            raw_volume = data.get("volume")

            # Ép kiểu an toàn (Safe Casting): Nếu None thì về 0.0
            try:
                change = float(raw_change) if raw_change is not None else 0.0
                price = float(raw_price) if raw_price is not None else 0.0
                volume = float(raw_volume) if raw_volume is not None else 0.0
            except (ValueError, TypeError):
                # Trường hợp dữ liệu bị lỗi format lạ, gán về 0 để không crash app
                change, price, volume = 0.0, 0.0, 0.0
            # -------------------------
            
            # Công thức ước lượng sức mạnh tác động:
            trading_value = price * volume
            impact_score = change * trading_value 

            all_stocks.append({
                "symbol": sym,
                "change": change,
                "score": impact_score
            })
            
        # Sắp xếp theo Impact Score thay vì chỉ theo % Change
        sorted_stocks = sorted(all_stocks, key=lambda x: x["score"], reverse=True)
        
        # Top 3 Tích cực (Score cao nhất)
        positive = [f"{s['symbol']} ({s['change']:+.2f}%)" for s in sorted_stocks[:3] if s['score'] > 0]
        
        # Top 3 Tiêu cực (Score thấp nhất - âm nhiều nhất)
        negative = [f"{s['symbol']} ({s['change']:+.2f}%)" for s in sorted_stocks[-3:] if s['score'] < 0]
        # Đảo ngược lại để mã giảm mạnh nhất đứng đầu list tiêu cực
        negative.reverse() 
        
        return positive, negative

    def prepare_report_input(self, raw_data: Dict) -> DailyReportInput:
        """
        Hàm tổng hợp cuối cùng: Biến dữ liệu thô thành Object sạch sẽ cho AI.
        """
        if not raw_data or not raw_data.get("index"):
            return None
            
        index_data = raw_data["index"]
        stocks_dict = raw_data["stocks"]
        
        # 1. Phân tích ngành
        sectors = self.analyze_sectors(stocks_dict)
        
        # 2. Top tác động
        pos_impact, neg_impact = self.get_top_impact(stocks_dict)
        
        # 3. Tạo Object kết quả
        return DailyReportInput(
            date="Hôm nay", 
            index=index_data,
            liquidity_comment="Chờ nhận định...",
            impact_positive=pos_impact,
            impact_negative=neg_impact,
            sectors=sectors,
            foreign=ForeignTrading(status="N/A", net_value=0, top_buy=[], top_sell=[]), 
            technical_score=0,
            technical_rating="N/A",
            pe_ratio=0.0,
            expert_comment=""
        )