# File: src/config.py

# 1. CẤU HÌNH HỆ THỐNG
APP_NAME = "Mirae Asset Daily Report Automation"
VERSION = "2.0.0"

# 2. DANH SÁCH NGÀNH (Giữ nguyên như cũ)
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

# 3. CẤU HÌNH AI (RAG PROMPT TEMPLATE)
# Lưu ý: Các biến trong ngoặc nhọn {} phải khớp chính xác với code trong ai_engine.py
# Không thực hiện phép tính (chia, nhân) trong ngoặc nhọn.

REPORT_PROMPT_TEMPLATE = """
Bạn là Chuyên viên phân tích cấp cao của Công ty Chứng khoán Mirae Asset Việt Nam (MAS).
Nhiệm vụ: Viết mục "NHẬN ĐỊNH THỊ TRƯỜNG" cho bản tin cuối ngày.

---
DỮ LIỆU ĐẦU VÀO (PHIÊN HÔM NAY - {date}):
- VN-Index: {vnindex_point} (Thay đổi: {vnindex_change} điểm, {vnindex_percent}%)
- Thanh khoản: ,với khối lượng giao dịch ở mức {liquidity_volume} triệu cổ phiếu, tương ứng với giá trị giao dịch hơn {liquidity_value} tỷ đồng.
- Nhận xét thanh khoản: {liquidity_comment}
- Độ rộng thị trường: {breadth_green} mã tăng / {breadth_red} mã giảm / {breadth_yellow} mã tham chiếu.
- Top Tác động:
    + Tích cực: {impact_positive}
    + Tiêu cực: {impact_negative}
- Diễn biến Nhóm ngành: {sector_performance}
- Giao dịch Khối ngoại: {foreign_status} {foreign_value} tỷ đồng.
    + Mua ròng: {foreign_buy_top}
    + Bán ròng: {foreign_sell_top}
- Góc nhìn Kỹ thuật: Điểm số {technical_score} ({technical_rating}). P/E thị trường: {pe_ratio}x.
- Ý chính/Tiêu đề gợi ý từ chuyên gia: "{expert_comment}"

---
CÁC BÀI BÁO CÁO MẪU TRONG QUÁ KHỨ CÓ BỐI CẢNH TƯƠNG TỰ (RAG CONTEXT):
{rag_context}

---
YÊU CẦU KHI VIẾT BÀI MỚI:
1.  **Tiêu đề:** Dựa vào "{expert_comment}" để đặt một tiêu đề giật tít (3-6 từ), sát với diễn biến.
2.  **Phong cách:** Bắt chước CẤU TRÚC CÂU và CÁCH DÙNG TỪ của các bài mẫu ở trên (Context), nhưng thay thế bằng số liệu của hôm nay.
3.  **Cấu trúc 4 đoạn:**
    *   *Đoạn 1:* Diễn biến phiên, điểm số, tâm lý thị trường và thanh khoản (Viết rõ khối lượng và giá trị).
    *   *Đoạn 2:* **Độ rộng thị trường** (Phải nhận xét: "nghiêng về bên mua/bán" hoặc "cân bằng" dựa trên số mã Tăng/Giảm). Sau đó liệt kê Top tác động và Diễn biến ngành.
    *   *Đoạn 2.5:* Diễn biến ngành. Phân tích ngành nào dẫn dắt, liệt kê Top 3 ngành tăng (nếu có) kèm mã cổ phiếu và ngược lại ngành nào tiêu cực, liệt kê Top 3 ngành giảm (nếu có) kèm mã cổ phiếu.
    *   *Đoạn 3:* Tổng giá trị mua/bán ròng và các mã tâm điểm.
    *   *Đoạn 4:* Nhận định ngắn gọn về điểm số kỹ thuật và P/E.
3.  **Ngôn ngữ:** Chuyên nghiệp, khách quan, sử dụng thuật ngữ tài chính (lực cầu, rung lắc, phân hóa, chốt lời...).

BẮT ĐẦU VIẾT BÁO CÁO:
"""