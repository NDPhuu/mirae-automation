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
                    change = data.get("change_percent", 0.0)
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
                top_losers=top_losers, # Sẽ fix logic hiển thị sau
                status=status
            ))
            
        # Sắp xếp các ngành: Ngành tăng mạnh nhất lên đầu
        return sorted(results, key=lambda x: x.avg_change, reverse=True)

    def get_top_impact(self, stock_data_dict: Dict[str, dict]) -> (List[str], List[str]):
        """
        Tìm Top mã tăng/giảm mạnh nhất trong danh sách theo dõi.
        (Tạm thời dùng % thay vì điểm đóng góp vì API chưa có điểm đóng góp)
        """
        all_stocks = []
        for sym, data in stock_data_dict.items():
            all_stocks.append({
                "symbol": sym,
                "change": data.get("change_percent", 0.0),
                "price": data.get("price", 0)
            })
            
        # Sắp xếp
        sorted_stocks = sorted(all_stocks, key=lambda x: x["change"], reverse=True)
        
        # Top 3 Tăng
        positive = [f"{s['symbol']} (+{s['change']}%)" for s in sorted_stocks[:3]]
        # Top 3 Giảm (Lấy cuối danh sách)
        negative = [f"{s['symbol']} ({s['change']}%)" for s in sorted_stocks[-3:]]
        
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
        # Lưu ý: Các trường như 'liquidity_comment', 'technical_score' 
        # sẽ được UI điền vào sau (Human-in-the-loop). Ở đây ta để giá trị mặc định.
        
        return DailyReportInput(
            date="Hôm nay", # Sẽ lấy ngày hiện tại
            index=index_data,
            liquidity_comment="Chờ nhận định...",
            impact_positive=pos_impact,
            impact_negative=neg_impact,
            sectors=sectors,
            foreign=ForeignTrading(status="N/A", net_value=0, top_buy=[], top_sell=[]), # Placeholder
            technical_score=0,
            technical_rating="N/A",
            pe_ratio=0.0,
            expert_comment=""
        )