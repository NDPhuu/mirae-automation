# File: src/config.py

# 1. CẤU HÌNH HỆ THỐNG
APP_NAME = "Mirae Asset Daily Report Automation"
VERSION = "1.0.0"

# 2. DANH SÁCH NGÀNH & MÃ ĐẠI DIỆN (SECTOR DEFINITION)
# Đây là logic "Bán tự động" mà chúng ta đã bàn.
# Bạn có thể thêm bớt mã tùy theo quan điểm của Mirae Asset.
SECTOR_MAPPING = {
    "Ngân hàng":               ["VCB","CTG","BID","TCB","VPB","MBB","LPB","ACB","HDB","STB","SHB","SSB","TPB","OCB","EIB","MSB","VIB","VAB"],
    "Chứng khoán":            ["SSI","HCM","BSI","TVB","AGR","ORS","MBS","VND","CTS","TVS"],
    "Bảo hiểm":               ["BVH","MIG","PVI","BMI","PGI"],
    "Bất động sản":           ["VIC","VHM","NVL","CKG","VRE","KBC","DXG","NLG","SCR","NHA","HDC","HPX","IJC","HQC","CRE","HAR","LDG"],
    "Xây dựng & Xây dựng công trình": ["CTD","FDC","C32","PC1","LGL","BAX","COM","SC5","BCE"],
    "Nguyên vật liệu (Thép, Xi măng)": ["HPG","HSG","NKG","BAX","SMC","LAF","HT1","SGH","TRC"],
    "Hóa chất & Phân bón":    ["DPM","DGC","DCM","BFC","CSV"],
    "Dệt may & Sợi":         ["TCM","DHC"],
    "Vận tải & Logistics":     ["HVN","VJC","PVT","VSC","GMD","VOS"],
    "Năng lượng (Dầu khí & Điện)": ["GAS","PLX","POW","NT2","PGC"],
    "Công nghệ & Viễn thông":  ["FPT","CMC","VNG"],
    "Tiêu dùng thiết yếu":    ["VNM","SAB","MCH","KDC","DHC","QNS","ASG"],
    "Tiêu dùng không thiết yếu": ["MWG","FRT","PNJ"],
    "Y tế & Dược phẩm":       ["DHG","IMP","OPC","TRA"],
    "Nông nghiệp & Thủy sản":  ["ANV","DBC","HNG","ASM"]
}


# 3. CẤU HÌNH AI (PROMPT TEMPLATE)
# Đây là prompt cơ bản (Few-shot đơn giản) dùng cho Giai đoạn 1.
REPORT_PROMPT_TEMPLATE = """
Bạn là chuyên viên phân tích cấp cao của Mirae Asset Việt Nam. 
Nhiệm vụ: Viết báo cáo nhận định thị trường hằng ngày dựa trên dữ liệu được cung cấp.

DỮ LIỆU THỊ TRƯỜNG:
- VN-Index: {vnindex_point} ({vnindex_change} điểm, {vnindex_percent}%)
- Thanh khoản: {liquidity_value} tỷ đồng (Đánh giá: {liquidity_comment})
- Độ rộng: {breadth_green} Tăng / {breadth_red} Giảm
- Khối ngoại: {foreign_status} {foreign_value} tỷ đồng.
    + Mua: {foreign_buy_top}
    + Bán: {foreign_sell_top}

DIỄN BIẾN DÒNG TIỀN & NHÓM NGÀNH:
- Top tác động tích cực: {impact_positive}
- Top tác động tiêu cực: {impact_negative}
- Nhóm ngành nổi bật: {sector_performance}

GÓC NHÌN KỸ THUẬT & CHUYÊN GIA:
- Điểm kỹ thuật Mirae: {technical_score} ({technical_rating})
- P/E thị trường: {pe_ratio}
- Nhận định bổ sung: {expert_comment}

YÊU CẦU VĂN PHONG:
- Chuyên nghiệp, khách quan, súc tích.
- Sử dụng thuật ngữ tài chính: "lực cầu", "áp lực chốt lời", "rung lắc", "phân hóa", "trụ đỡ".
- Cấu trúc bài viết:
    1. Diễn biến phiên giao dịch (Tóm tắt index, thanh khoản).
    2. Dòng tiền và Nhóm ngành (Phân tích sâu các mã/ngành tác động).
    3. Giao dịch Khối ngoại.
    4. Góc nhìn kỹ thuật và Dự báo phiên tới.
"""