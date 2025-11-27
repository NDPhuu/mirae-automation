from pydantic import BaseModel, Field
from typing import List, Optional

# 1. Cấu trúc cho Cổ phiếu Tác động (Impact Stock)
# Kết hợp dữ liệu từ 2 nguồn như bạn yêu cầu:
# - contribution_point: Lấy từ FireAnt (Điểm đóng góp)
# - change_percent: Lấy từ Bảng giá (% Tăng/Giảm)
class StockImpact(BaseModel):
    ticker: str = Field(..., description="Mã cổ phiếu, ví dụ: VCB")
    change_percent: float = Field(..., description="% Tăng giảm giá (từ bảng điện)")
    contribution_point: float = Field(..., description="Điểm đóng góp vào Index (từ FireAnt)")
    price: Optional[float] = Field(None, description="Giá đóng cửa (nghìn đồng)")

# 2. Cấu trúc cho Nhóm ngành (Sector)
class SectorInfo(BaseModel):
    name: str = Field(..., description="Tên ngành, ví dụ: Ngân hàng")
    change_percent: float = Field(..., description="% Thay đổi trung bình của ngành")
    top_stocks: List[str] = Field(..., description="Danh sách mã tiêu biểu, ví dụ: ['VCB', 'BID']")

# 3. Cấu trúc cho Giao dịch Khối ngoại (Foreign Trade)
class ForeignDetail(BaseModel):
    ticker: str
    value: float = Field(..., description="Giá trị giao dịch (Tỷ đồng)")

class ForeignTrade(BaseModel):
    status: str = Field(..., description="Mua ròng hay Bán ròng")
    net_value: float = Field(..., description="Tổng giá trị ròng (Tỷ đồng)")
    top_buying: List[ForeignDetail] = Field(..., description="Top mã Mua ròng")
    top_selling: List[ForeignDetail] = Field(..., description="Top mã Bán ròng")

# 4. Cấu trúc Tổng quan Thị trường (Market Overview)
class MarketOverview(BaseModel):
    # Chỉ số VN-Index
    index_value: float
    change_point: float
    change_percent: float
    
    # Thanh khoản
    total_volume: float = Field(..., description="Tổng khối lượng (Triệu cổ phiếu)")
    total_value: float = Field(..., description="Tổng giá trị (Tỷ đồng)")
    ma20_volume: float = Field(..., description="Trung bình khối lượng 20 phiên")
    liquidity_assessment: str = Field(..., description="Đánh giá: Thấp hơn/Cao hơn MA20")
    
    # Độ rộng thị trường
    gainers: int = Field(..., description="Số mã Tăng")
    losers: int = Field(..., description="Số mã Giảm")
    unchanged: int = Field(..., description="Số mã Tham chiếu")

# 5. Cấu trúc Dữ liệu Đầu vào Tổng hợp (Input cho AI)
class DailyReportData(BaseModel):
    report_date: str
    overview: MarketOverview
    
    # List các mã tác động (Đã sort sẵn Tích cực/Tiêu cực)
    impact_positive: List[StockImpact]
    impact_negative: List[StockImpact]
    
    # List nhóm ngành (Đã sort theo xu hướng Index)
    top_sectors: List[SectorInfo]
    
    foreign_trade: ForeignTrade
    
    # Phần nhận định thủ công & Kỹ thuật
    chart_description: str = Field(..., description="Mô tả diễn biến phiên (Sáng/Chiều)")
    mirae_score: int = Field(..., description="Điểm kỹ thuật (-7 đến +7)")
    technical_status: str = Field(..., description="TIÊU CỰC / TRUNG TÍNH / TÍCH CỰC")
    pe_ratio: float