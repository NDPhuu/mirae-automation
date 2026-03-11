# File: src/services/market_logic.py
from typing import List, Dict
from src.models import SectorPerformance, ForeignTrading, DailyReportInput, StockData, MarketIndex
from src.config import SECTOR_MAPPING
from src.services.ssi_service import SSIService

class MarketLogic:
    def __init__(self):
        # Khởi tạo SSI Service
        self.ssi_service = SSIService()

    def analyze_sectors(self, stocks_dict: Dict[str, StockData]) -> List[SectorPerformance]:
        """
        Tính toán hiệu suất nhóm ngành dựa trên dữ liệu gộp.
        """
        results = []
        
        for sector_name, symbols in SECTOR_MAPPING.items():
            sector_stocks = []
            total_change = 0.0
            count = 0
            
            for sym in symbols:
                stock = stocks_dict.get(sym)
                if stock:
                    change = stock.change_percent
                    sector_stocks.append({"symbol": sym, "change": change})
                    total_change += change
                    count += 1
            
            if count == 0:
                continue

            # Tính trung bình ngành
            avg_change = total_change / count
            
            # Tìm mã Tăng/Giảm mạnh nhất để hiển thị
            sorted_stocks = sorted(sector_stocks, key=lambda x: x["change"], reverse=True)
            
            top_gainers = [s["symbol"] for s in sorted_stocks if s["change"] > 0][:3]
            top_losers = [s["symbol"] for s in sorted_stocks if s["change"] < 0][-3:]
            top_losers.reverse() # Đảo ngược để mã giảm sâu nhất đứng đầu
            
            # Đánh giá trạng thái
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
            
        # Sắp xếp ngành tăng mạnh nhất lên đầu
        return sorted(results, key=lambda x: x.avg_change, reverse=True)

    def get_top_impact(self, stocks_dict: Dict[str, StockData], vnindex_point: float = 0) -> (List[str], List[str]):
        """
        Tìm Top mã tác động chỉ số.
        Công thức chuẩn market-cap formula.
        """
        all_stocks = []
        market_caps = {}
        
        # Bước 1: Tính Market Cap cho từng mã
        for sym, stock in stocks_dict.items():
            price = float(stock.price or 0)
            shares = int(stock.shares or 0)
            market_caps[sym] = price * shares
        
        total_market_cap = sum(market_caps.values())
        
        # Nếu không có total_market_cap (do thiếu listed_shares), không thể tính chính xác
        if total_market_cap == 0:
            return [], []
        
        for sym, stock in stocks_dict.items():
            try:
                price = float(stock.price) if stock.price else 0.0
                ref_price = float(stock.ref_price) if stock.ref_price else 0.0
                change = float(stock.change_percent) if stock.change_percent else 0.0
                
            except (ValueError, TypeError):
                price, ref_price, change = 0.0, 0.0, 0.0
            
            # Step 2: Weight
            weight = market_caps[sym] / total_market_cap
            
            # Step 3: Pct Change
            pct_change = (price - ref_price) / ref_price if ref_price > 0 else 0.0
            
            # Step 4: Pct Impact
            pct_impact = weight * pct_change
            
            # Step 5: Impact Points
            impact_points = vnindex_point * pct_impact

            all_stocks.append({
                "symbol": sym,
                "change": change,  # Lưu lại percentage change để hiển thị
                "impact_points": impact_points
            })
            
        # Sắp xếp theo Impact Points (Điểm tác động chỉ số)
        sorted_stocks = sorted(all_stocks, key=lambda x: x["impact_points"], reverse=True)
        
        # Top 3 Tích cực, hiển thị change_percent theo yêu cầu (symbol (+change%))
        positive = [f"{s['symbol']} ({s['change']:+.2f}%)" for s in sorted_stocks[:3] if s['impact_points'] > 0]
        
        # Top 3 Tiêu cực, cũng hiển thị change_percent
        negative = [f"{s['symbol']} ({s['change']:+.2f}%)" for s in sorted_stocks[-3:] if s['impact_points'] < 0]
        negative.reverse()
        
        return positive, negative
        
        return positive, negative

    def analyze_foreign(self, stocks_dict: Dict[str, StockData]) -> ForeignTrading:
        """Phân tích dữ liệu khối ngoại. SSI trả về giá trị VND gốc → chia 1 tỷ."""
        total_net_value = 0.0
        foreign_stats = []

        for sym, stock in stocks_dict.items():
            buy_val = float(stock.f_buy_val or 0)
            sell_val = float(stock.f_sell_val or 0)
            
            if buy_val == 0 and sell_val == 0:
                continue
            
            # SSI luôn trả về đơn vị VND gốc → chia 1 tỷ để ra Tỷ đồng
            buy_ty = buy_val / 1_000_000_000
            sell_ty = sell_val / 1_000_000_000
            
            net_val = buy_ty - sell_ty
            
            if round(net_val, 1) != 0:
                total_net_value += net_val
                foreign_stats.append({"symbol": sym, "net": net_val})

        # Sắp xếp theo giá trị ròng
        sorted_foreign = sorted(foreign_stats, key=lambda x: x["net"], reverse=True)
        
        # Top 3 Mua ròng (lớn nhất)
        top_buy = [f"{s['symbol']} (+{s['net']:.0f} tỷ)" for s in sorted_foreign[:3] if s['net'] > 0]
        
        # Top 3 Bán ròng (âm nhất)
        top_sell_raw = [s for s in sorted_foreign if s['net'] < 0][-3:]
        top_sell_raw.reverse()
        top_sell = [f"{s['symbol']} (-{abs(s['net']):.0f} tỷ)" for s in top_sell_raw]
        
        status = "MUA RÒNG" if total_net_value > 0 else "BÁN RÒNG"
        
        return ForeignTrading(
            status=status,
            net_value=round(abs(total_net_value), 2),
            top_buy=top_buy,
            top_sell=top_sell
        )
        
    def prepare_report_input(self, index_data: MarketIndex, stocks_dict: Dict[str, StockData]) -> DailyReportInput:
        """Hàm tổng hợp cuối cùng"""
        if not index_data or not stocks_dict:
            return None
            
        sectors = self.analyze_sectors(stocks_dict)
        pos_impact, neg_impact = self.get_top_impact(stocks_dict, index_data.point)
        
        # Gọi hàm phân tích khối ngoại từ DataAggregator
        foreign_data = self.analyze_foreign(stocks_dict)
        
        return DailyReportInput(
            date="Hôm nay", 
            index=index_data,
            liquidity_comment="Chờ nhận định...",
            impact_positive=pos_impact,
            impact_negative=neg_impact,
            sectors=sectors,
            foreign=foreign_data,
            technical_score=0,
            technical_rating="N/A",
            pe_ratio=0.0,
            expert_comment=""
        )