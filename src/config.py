# File: src/config.py

# 1. CẤU HÌNH HỆ THỐNG
APP_NAME = "Mirae Asset Daily Report Automation"
VERSION = "2.2.1"

# 2. DANH SÁCH NGÀNH (CẬP NHẬT MỚI)
SECTOR_MAPPING = {
    "Ô tô và phụ tùng": ["VVS", "CSM", "CTF", "DRC", "HAX", "HHS", "HTL", "SRC", "SVC", "TMT"],
    "Xây dựng và Vật liệu": ["CCC", "TSA", "GMH", "RYG", "ACC", "ADP", "BCE", "BMP", "C32", "C47", "CDC", "CIG", "CII", "CRC", "CTD", "CTI", "CTR", "CVT", "DPG", "DC4", "DHA", "DLG", "DXV", "EVG", "FCM", "FCN", "GEL", "HID", "HHV", "HAS", "HT1", "HTI", "HU1", "HVH", "KSB", "LBM", "LCG", "LGC", "LM8", "MDG", "NAV", "NHA", "NNC", "PC1", "PHC", "PTC", "SC5", "TCR", "THG", "TLD", "TNT", "TCD", "HUB", "VCG", "VGC", "VNE", "VSI"],
    "Hàng công nghiệp": ["SBG", "APH", "MCP", "TDP"],
    "Quỹ đầu tư": ["FUCTVGF3", "FUEIP100", "FUEKIV30", "FUCTVGF4", "FUEDCMID", "FUEKIVFS", "FUEMAVND", "FUEFCV50", "FUEBFVND", "FUCTVGF5", "FUEKIVND", "FUEABVND", "FUETCC50", "FUETPVND", "FUESSV50", "E1VFVN30", "FUESSVFL", "FUEMAV30", "FUESSV30", "FUEVFVND", "FUEVN100", "FUCVREIT"],
    "Công nghiệp nặng": ["NO1", "L10", "SRF"],
    "Hóa chất": ["AAA", "ABS", "HII", "BFC", "BRC", "CSV", "DCM", "DGC", "DPM", "DPR", "DTT", "HCD", "HRC", "NHH", "PLP", "PHR", "SFG", "TNC", "TPC", "TRC", "TSC", "VAF", "VFG", "VPS", "GVR"],
    "Sản xuất thực phẩm": ["AAM", "ABT", "ACL", "ANT", "ANV", "ASM", "BAF", "CMX", "DBC", "FMC", "HAG", "HSL", "HPA", "IDI", "KDC", "LAF", "LSS", "MCM", "MCH", "MSN", "NSC", "PAN", "DAT", "SBT", "SSC", "TCO", "VHC", "VNM"],
    "Hàng cá nhân": ["AAT", "STK", "ADS", "EVE", "GIL", "HTG", "KMR", "LIX", "PNJ", "MSH", "SVD", "TCM", "TVT"],
    "Tư vấn & Hỗ trợ Kinh doanh": ["ABR", "TV2"],
    "Ngân hàng": ["ACB", "BID", "CTG", "EIB", "HDB", "KLB", "LPB", "MBB", "MSB", "NAB", "OCB", "SSB", "SHB", "STB", "TCB", "TPB", "VAB", "VCB", "VIB", "VPB"],
    "Phân phối thực phẩm & dược phẩm": ["AFX"],
    "Dịch vụ tài chính": ["AGR", "APG", "VPX", "BCG", "BSI", "CTS", "DSC", "DSE", "EVF", "FTS", "HCM", "OGC", "ORS", "SSI", "TCX", "TCI", "TVB", "TVS", "VCI", "VDS", "VIX", "VND", "VCK"],
    "Bất động sản": ["AGG", "BCM", "CCL", "CRE", "CKG", "D2D", "DIG", "DRH", "DTA", "DXG", "DXS", "FDC", "FIR", "HPX", "HAR", "HDC", "HDG", "TCH", "HQC", "HTN", "CRV", "IJC", "ITC", "KBC", "KDH", "KHG", "KOS", "LDG", "LGL", "LHG", "NBB", "VHM", "NLG", "NVL", "NTC", "NTL", "NVT", "PDR", "PTL", "QCG", "SCR", "SGR", "SIP", "SZC", "SJS", "SZL", "TAL", "TDC", "TDH", "TEG", "TIP", "TIX", "TN1", "VIC", "VPH", "VPI", "VRC", "VRE"],
    "Lâm nghiệp và Giấy": ["ACG", "DHC", "GTA", "HAP", "HHP", "PTB", "SAV", "TTF", "VID"],
    "Vận tải": ["ASG", "CLL", "DVP", "GMD", "GSP", "HAH", "HTV", "ILB", "MHC", "NCT", "PDN", "PDV", "PJT", "PVT", "PVP", "QNP", "SGN", "SFI", "STG", "TCL", "TMS", "VIP", "VNL", "VOS", "VSC", "VTO", "VTP"],
    "Nước & Khí đốt": ["ASP", "BWE", "CCI", "CLW", "CNG", "GAS", "PGC", "PGD", "PMG", "SFC", "TDG", "TDM", "TDW"],
    "Bia và đồ uống": ["BHN", "NAF", "SAB", "SMB", "VCF"],
    "Bảo hiểm phi nhân thọ": ["BIC", "BMI", "MIG", "PGI"],
    "Dược phẩm": ["DBD", "DBT", "DCL", "DHG", "DMC", "FIT", "IMP", "OPC", "SPM", "TRA", "VDP", "VMD"],
    "Hàng gia dụng": ["BKG", "DQC", "GDT", "RAL", "TLG"],
    "Khai khoáng": ["BMC", "DHM", "VPG", "YBM"],
    "Sản xuất Dầu khí": ["BSR", "PLX"],
    "Sản xuất & Phân phối Điện": ["BTP", "CHP", "TTE", "DRL", "PGV", "GHC", "GEG", "HNA", "KHP", "NT2", "PPC", "POW", "REE", "SBA", "SHP", "SJD", "SMA", "S4A", "TBC", "TMP", "TTA", "UIC", "VPD", "VSH"],
    "Bán lẻ": ["BTT", "CMV", "COM", "DGW", "FRT", "MWG", "PET", "PIT", "SBV", "SVT", "AST"],
    "Bảo hiểm nhân thọ": ["BVH"],
    "Thiết bị và Dịch vụ Y tế": ["TNH", "JVC"],
    "Thuốc lá": ["CLC"],
    "Truyền thông": ["ADG", "PNC", "YEG"],
    "Phần mềm & Dịch vụ Máy tính": ["CMG", "ICT", "FPT", "ITD", "SGT"],
    "Du lịch & Giải trí": ["DAH", "DSN", "SCS", "SKG", "TCT", "VJC", "HVN", "VNG", "VNS", "VPL"],
    "Kim loại": ["DTL", "HMC", "HPG", "HSG", "NKG", "SHA", "SHI", "SMC", "TLH", "TNI", "VCA"],
    "Thiết bị và Phần cứng": ["ELC", "SAM", "ST8"],
    "Điện tử & Thiết bị điện": ["GEX", "GEE", "PAC", "TYA", "VTB"],
    "Hàng hóa giải trí": ["NHT"],
    "Thiết bị, Dịch vụ và Phân phối Dầu khí": ["PVD"],
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
    *   *Đoạn 2:* **Độ rộng thị trường** (Phải nhận xét: "nghiêng về bên mua/bán" hoặc "cân bằng" dựa trên số mã Tăng/Giảm). Sau đó liệt kê Top tác động.
    *   *Đoạn 2.5:* Diễn biến ngành. Viết thật RÚT GỌN. Chỉ liệt kê tối đa 3 ngành tích cực nhất kèm theo tối đa 3 mã nổi bật mỗi ngành, và tối đa 3 ngành tiêu cực nhất kèm theo tối đa 3 mã nổi bật. Không liệt kê lan man. Ví dụ: "Dòng tiền tập trung vào nhóm [Ngành 1] (mã 1, mã 2), [Ngành 2] (mã 3), trong khi [Ngành 3] (mã 4) sụt giảm mạnh". Dựa tuyệt đối vào dữ liệu được cung cấp.
    *   *Đoạn 3:* Tổng giá trị mua/bán ròng và các mã tâm điểm.
    *   *Đoạn 4:* Nhận định ngắn gọn về điểm số kỹ thuật và P/E.
4.  **Ngôn ngữ:** Chuyên nghiệp, khách quan, sử dụng thuật ngữ tài chính (lực cầu, rung lắc, phân hóa, chốt lời...).

BẮT ĐẦU VIẾT BÁO CÁO:
"""