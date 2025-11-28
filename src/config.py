# File: src/config.py

# 1. CẤU HÌNH HỆ THỐNG
APP_NAME = "Mirae Asset Daily Report Automation"
VERSION = "1.0.0"

# 2. DANH SÁCH NGÀNH & MÃ ĐẠI DIỆN (SECTOR DEFINITION)
# Đây là logic "Bán tự động" mà chúng ta đã bàn.
# Bạn có thể thêm bớt mã tùy theo quan điểm của Mirae Asset.
SECTOR_MAPPING = {
    "Ngân hàng": ["VCB", "BID", "CTG", "MBB", "ACB", "TCB", "VPB", "STB"],
    "Chứng khoán": ["SSI", "VND", "VCI", "HCM", "MBS", "SHS", "FTS"],
    "Bất động sản": ["VHM", "VIC", "VRE", "NVL", "PDR", "DIG", "DXG", "KDH"],
    "Thép": ["HPG", "HSG", "NKG"],
    "Dầu khí": ["GAS", "PLX", "PVD", "PVS", "BSR"],
    "Bán lẻ": ["MWG", "FRT", "DGW", "PNJ"],
    "Thủy sản": ["VHC", "ANV", "IDI"],
    "Khu công nghiệp": ["KBC", "IDC", "SZC", "VGC"],
    "Đầu tư công": ["VCG", "HHV", "LCG", "KSB"]
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