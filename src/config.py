# File: src/config.py

# 1. CẤU HÌNH HỆ THỐNG
APP_NAME = "Mirae Asset Daily Report Automation"
VERSION = "2.2.1"

# 2. DANH SÁCH NGÀNH
SECTOR_MAPPING = {
  "Ngân hàng": [
    "ACB", "BID", "CTG", "EIB", "HDB", "LPB", "MBB", "MSB", "NAB", 
    "OCB", "SHB", "SSB", "STB", "TCB", "TPB", "VCB", "VIB", "VPB"
  ],
  "Chứng khoán & Dịch vụ tài chính": [
    "AGR", "APG", "BCG", "BSI", "CTS", "DSE", "DSC", "EVF", "FIT", 
    "FTS", "HCM", "MBS", "OGC", "ORS", "SSI", "TCI", "TVB", "TVS", 
    "VCI", "VDS", "VIX", "VND"
  ],
  "Quỹ ETF & Chứng chỉ quỹ": [
    "E1VFVN30", "FUCVREIT", "FUCTVGF3", "FUCTVGF4", "FUCTVGF5", 
    "FUEDCMID", "FUEABVND", "FUEBFVND", "FUEFCV50", "FUEIP100", 
    "FUEKIV30", "FUEKIVFS", "FUEKIVND", "FUEMAV30", "FUEMAVND", 
    "FUESSV30", "FUESSV50", "FUESSVFL", "FUEVFVND", "FUEVN100"
  ],
  "Bất động sản": [
    "AGG", "BCM", "CCL", "CKG", "CRE", "D2D", "DIG", "DRH", "DTA", 
    "DXG", "DXS", "FDC", "FIR", "HAR", "HDC", "HDG", "HPX", "HQC", 
    "IJC", "ITA", "ITC", "KBC", "KDH", "KHG", "KOS", "LDG", "LEC", 
    "LGL", "LHG", "NBB", "NLG", "NTL", "NVL", "NVT", "PDR", "PTL", 
    "QCG", "SCR", "SGR", "SIP", "SJS", "SZC", "SZL", "TCH", "TDC", 
    "TDH", "TEG", "TIP", "TIX", "TLD", "TN1", "VHM", "VIC", "VPH", 
    "VPI", "VRC", "VRE", "VSI"
  ],
  "Xây dựng & Vật liệu xây dựng": [
    "ACC", "ADP", "BCE", "BMP", "C32", "C47", "CDC", "CIG", "CII", 
    "CRC", "CTD", "CTI", "CTR", "CVT", "DC4", "DHA", "DPG", "DXV", 
    "EVG", "FCM", "FCN", "GMH", "HAS", "HID", "HHV", "HT1", "HTI", 
    "HTN", "HU1", "HUB", "HVH", "HVX", "KPF", "LBM", "LCG", "LGC", 
    "LM8", "MDG", "NAV", "NHA", "NNC", "PC1", "PHC", "PTC", "SC5", 
    "TCD", "TCR", "THG", "VCG", "VGC", "VNE"
  ],
  "Thép & Tài nguyên cơ bản": [
    "ACG", "BMC", "DHC", "DHM", "DTL", "GTA", "HAP", "HHP", "HMC", 
    "HPG", "HSG", "KSB", "NKG", "PTB", "SAV", "SHA", "SHI", "SMC", 
    "SVT", "TLH", "TNA", "TNI", "TNT", "TTF", "VCA", "VID", "VPG", 
    "YBM"
  ],
  "Thủy sản": [
    "AAM", "ABT", "ACL", "ANV", "ASM", "CMX", "DAT", "FMC", "IDI", "VHC"
  ],
  "Nông nghiệp (Chăn nuôi, Giống, Gạo)": [
    "AGM", "BAF", "DBC", "HAG", "HSL", "NSC", "PAN", "SSC"
  ],
  "Tiêu dùng thiết yếu (Sữa, Đường, Bia, Thực phẩm chế biến)": [
    "BBC", "BHN", "KDC", "LAF", "LSS", "MCM", "MSN", "NAF", "QNS", 
    "SAB", "SBT", "SMB", "VCF", "VNM"
  ],
  "Hóa chất & Phân bón": [
    "AAA", "ABS", "BFC", "BRC", "CSV", "DCM", "DGC", "DPM", "DPR", 
    "DTT", "GVR", "HCD", "HII", "HRC", "NHH", "PHR", "PLP", "RDP", 
    "SFG", "SJF", "TNC", "TPC", "TRC", "TSC", "VAF", "VFG", "VPS"
  ],
  "Bán lẻ": [
    "AST", "BTT", "BVH", "CMV", "COM", "DGW", "FRT", "MWG", "PET", 
    "PIT", "SBV"
  ],
  "Vận tải, Cảng biển & Logistics": [
    "ABR", "ASG", "CLL", "DVP", "GEE", "GEX", "GMD", "GSP", "HAH", 
    "HTV", "ILB", "L10", "MHC", "NCT", "NO1", "PAC", "PDN", "PJT", 
    "PVP", "PVT", "QNP", "SFI", "SGN", "SRF", "STG", "SVI", "TCL", 
    "TCO", "TDP", "TMS", "TV2", "TYA", "VIP", "VNL", "VOS", "VSC", 
    "VTB", "VTO", "VTP"
  ],
  "Năng lượng & Tiện ích": [
    "ASP", "BTP", "BWE", "CCI", "CHP", "CLW", "CNG", "DRL", "GAS", 
    "GEG", "HNA", "KHP", "NT2", "PGC", "PGD", "PGV", "PMG", "POW", 
    "PPC", "PSH", "REE", "S4A", "SBA", "SFC", "SHP", "SJD", "SMA", 
    "TBC", "TDG", "TDM", "TDW", "TMP", "TTA", "TTE", "UIC", "VPD", 
    "VSH"
  ],
  "Dầu khí": [
    "PLX", "PVD"
  ],
  "Công nghệ & Viễn thông": [
    "CMG", "ELC", "FPT", "ICT", "ITD", "SAM", "SGT", "ST8"
  ],
  "Y tế & Dược phẩm": [
    "DBD", "DBT", "DCL", "DHG", "DMC", "IMP", "JVC", "OPC", "SPM", 
    "TNH", "TRA", "VDP", "VMD"
  ],
  "Bảo hiểm": [
    "BIC", "BMI", "BVH", "MIG", "PGI"
  ],
  "Du lịch & Giải trí": [
    "DAH", "DSN", "HVN", "SCS", "SKG", "TCT", "VJC", "VNG", "VNS"
  ],
  "Ô tô & Phụ tùng": [
    "CSM", "CTF", "DRC", "HAX", "HHS", "HTL", "SRC", "SVC", "TMT"
  ],
  "Hàng cá nhân & Gia dụng": [
    "AAT", "ADS", "APH", "BKG", "CLC", "DQC", "EVE", "GDT", "GIL", 
    "GMC", "HTG", "KMR", "LIX", "MCP", "MSH", "NHT", "PNJ", "RAL", 
    "SBG", "STK", "SVD", "TCM", "TLG", "TVT"
  ],
  "Truyền thông": [
    "ADG", "PNC", "YEG"
  ]
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