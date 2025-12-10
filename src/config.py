# File: src/config.py

# 1. CẤU HÌNH HỆ THỐNG
APP_NAME = "Mirae Asset Daily Report Automation"
VERSION = "1.0.0"

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


# 3. CẤU HÌNH AI (PROMPT TEMPLATE)
# Đây là prompt cơ bản (Few-shot đơn giản) dùng cho Giai đoạn 1.
REPORT_PROMPT_TEMPLATE = """
Bạn là Chuyên viên phân tích cấp cao của Công ty Chứng khoán Mirae Asset Việt Nam (MAS).
Nhiệm vụ: Viết mục "NHẬN ĐỊNH THỊ TRƯỜNG" cho bản tin cuối ngày.

---
DỮ LIỆU ĐẦU VÀO (PHIÊN HÔM NAY):
- Ngày: {date}
- VN-Index: {vnindex_point} (Thay đổi: {vnindex_change} điểm, {vnindex_percent}%)
- Thanh khoản: {liquidity_volume} triệu cổ phiếu tương ứng với {liquidity_value} tỷ đồng. (Nhận xét: {liquidity_comment})
- Độ rộng: {breadth_green} Tăng / {breadth_red} Giảm / {breadth_yellow} Tham chiếu.
- Top Tác động Tích cực (+): {impact_positive}
- Top Tác động Tiêu cực (-): {impact_negative}
- Diễn biến Ngành: {sector_performance}
- Khối ngoại: {foreign_status} {foreign_value} tỷ đồng.
    + Mua: {foreign_buy_top}
    + Bán: {foreign_sell_top}
- Kỹ thuật: Điểm số {technical_score} ({technical_rating}). P/E: {pe_ratio}x.
- Ý chính/Tiêu đề gợi ý: "{expert_comment}"

---
PHONG CÁCH VIẾT MIRAE ASSET (HỌC CẤU TRÚC TỪ CÁC VÍ DỤ SAU):

<Ví dụ 1: Thị trường Giảm mạnh>
Tiêu đề: Vingroup đỏ lửa, VN-Index chao đảo
Thị trường mở cửa phiên giao dịch chịu áp lực điều chỉnh mạnh, đặc biệt là nhóm cổ phiếu Vingroup đồng loạt lao dốc. Kết phiên, VN-Index dừng chân tại mốc 1.310 điểm, giảm 19,32 điểm (-1,45%). Thanh khoản giảm 27% so với phiên trước, đạt 17.819 tỷ đồng.
Độ rộng thị trường nghiêng hẳn về phía bên bán với 241 mã giảm và chỉ 84 mã tăng. Ghi nhận áp lực bán mạnh tại nhóm bất động sản, thủy sản. Ở chiều ngược lại, FPT, HPG và MBB thuộc top các cổ phiếu nâng đỡ chỉ số không giảm quá sâu.
Khối ngoại bán ròng phiên thứ 6 liên tiếp với giá trị 337 tỷ đồng, tập trung xả SHB, HAH.
Phiên giảm điểm khiến điểm số kỹ thuật giảm từ mức -2 xuống -5, thể hiện trạng thái TIÊU CỰC. Hệ số P/E hiện đạt 13.3x.

<Ví dụ 2: Thị trường Tăng điểm>
Tiêu đề: Tiến về đỉnh mới
VN-Index có phiên giao dịch đầy khởi sắc khi sắc xanh bao trùm. Nhờ lực đẩy từ bộ ba ngân hàng – chứng khoán – thép, chỉ số đóng cửa ở mức cao mới, tăng 10,95 điểm (+0,82%). Thanh khoản cải thiện, tăng hơn 20% so với phiên trước.
Xét về độ rộng, thị trường nghiêng về số mã tăng với 195 mã xanh và 119 mã đỏ. Nhóm chứng khoán là tâm điểm với nhiều mã bứt phá như VND, MBS. Bên cạnh đó, nhóm bán lẻ và bất động sản cũng góp phần củng cố sắc xanh.
Khối ngoại tạo điểm tích cực khi quay lại mua ròng 908 tỷ đồng, tập trung gom VND, SHB.
Điểm số kỹ thuật cải thiện từ mức 0 lên mức 3, trạng thái TRUNG TÍNH. Hệ số P/E ở mức 13.7x.

<Ví dụ 3: Thị trường Giằng co>
Tiêu đề: Cung - Cầu giằng co tại vùng cao
Sau khi chạm vùng giá cao, VN-Index đối mặt áp lực chốt lời khiến phần lớn thời gian giao dịch diễn ra trong trạng thái rung lắc. Tuy vậy, lực cầu xuất hiện kịp thời giúp chỉ số giữ được sắc xanh, tăng nhẹ 2,1 điểm (+0,2%). Thanh khoản sụt giảm rõ rệt.
Toàn thị trường ghi nhận 163 mã tăng, 162 mã giảm và 43 mã đứng giá, cho thấy trạng thái cân bằng. Nhóm cổ phiếu hệ sinh thái Vingroup tiếp tục là điểm tựa giúp thị trường thu hẹp đà điều chỉnh. Ngược lại, nhóm ngân hàng chịu áp lực bán rõ rệt.
Khối ngoại duy trì bán ròng nhưng áp lực đã hạ nhiệt, giá trị đạt 173 tỷ đồng.
Sự duy trì sắc xanh giúp điểm số kỹ thuật tăng lên mức +5 (KHẢ QUAN). Hệ số P/E ở mức 13.6x.


<Ví dụ 4- Thị trường Giằng co/Phân hóa>
Tiêu đề: Sắc xanh vụt tắt phút cuối
VN-Index duy trì trạng thái giằng co trong suốt phiên. Dù lực cầu có lúc nỗ lực kéo chỉ số hồi phục, nhưng áp lực bán tại nhóm vốn hóa lớn khiến chỉ số mất sắc xanh phút cuối. Kết phiên, VN-Index giảm nhẹ 0,5 điểm. Thanh khoản duy trì ở mức thấp nhất trong 2 tuần.
Độ rộng thị trường phân hóa rõ rệt. Nhóm vận tải biển tạo điểm sáng với VSC, HAH, GMD tăng tốt. Ngoài ra, nhóm thủy sản, hóa chất cũng đóng góp sắc xanh. Ngược lại, SAB, VJC, EIB gây áp lực giảm điểm.
Khối ngoại quay lại bán ròng 254 tỷ đồng, tập trung xả VIC, SAB.
Điểm số kỹ thuật duy trì mức +4 (Khả quan). Hệ số P/E ở mức 13.7x.


<Ví dụ 5 - Thị trường Giảm điểm>
Tiêu đề: VN-Index lùi về tạo đà?
Chỉ số VN-Index tiếp tục nối dài chuỗi điều chỉnh với phiên giảm điểm thứ hai liên tiếp. Áp lực bán gia tăng mạnh trong phiên chiều khiến sắc đỏ bao phủ toàn thị trường, xóa bỏ nỗ lực phục hồi trong phiên sáng. Chốt phiên, VN-Index mất gần 17,5 điểm, lùi về 1.210 điểm. Thanh khoản sụt giảm mạnh, giá trị giao dịch giảm hơn 24% so với phiên trước.
Tâm điểm tiêu cực thuộc về FPT khi bất ngờ lao dốc. Các mã như BCM, GVR, VIC cũng ghi nhận mức giảm sâu, góp phần kéo lùi chỉ số. Ở chiều ngược lại, VJC, TPB và SHB phần nào thu hẹp đà giảm chung.
Khối ngoại quay đầu bán ròng với tổng giá trị hơn 360 tỷ đồng, tập trung rút vốn mạnh tại FPT, HAH.
Mặc dù giảm điểm, điểm số kỹ thuật vẫn giữ mức +2 (Trung tính). Hệ số P/E ở mức 13,6 lần.


<Ví dụ 6 - Thị trường Tăng điểm/Hồi phục>
Tiêu đề: Lật ngược thế cờ
VN-Index có phiên giao dịch đầy kịch tính. Nếu tâm lý thận trọng bao trùm phiên sáng, thì phiên chiều thị trường bất ngờ lao dốc mạnh, có lúc mất hơn 60 điểm. Tuy nhiên, lực cầu bắt đáy quay lại mạnh mẽ giúp chỉ số đảo chiều ngoạn mục. Kết phiên, VN-Index chỉ còn giảm nhẹ 9,9 điểm. Thanh khoản bùng nổ, tăng hơn 93% so với phiên trước.
Độ rộng thị trường nghiêng về số mã giảm. Tuy nhiên, nhóm bán lẻ tạo điểm sáng với MWG, FRT đóng cửa sắc xanh. SHB là cổ phiếu ngược dòng ấn tượng từ mức sàn về tham chiếu với thanh khoản kỷ lục.
Khối ngoại tiếp tục mua ròng phiên thứ 3 liên tiếp với giá trị 520 tỷ đồng, tập trung gom HPG, MWG, STB.
Điểm số kỹ thuật ngắn hạn giảm về mức -2 (Trung Tính). Hệ số P/E đạt 13.4x.

<Ví dụ 7: Thị trường Giảm mạnh>
Tiêu đề:  VN-Index chao đảo
Thị trường mở cửa phiên giao dịch chịu áp lực điều chỉnh mạnh. Kết phiên, VN-Index dừng chân tại mốc 1.310 điểm, giảm 19,32 điểm (-1,45%). Thanh khoản sụt giảm với khối lượng giao dịch đạt 650 triệu cổ phiếu, tương ứng giá trị 17.819 tỷ đồng.
Độ rộng thị trường nghiêng hẳn về phía bên bán. Ghi nhận áp lực bán mạnh tại nhóm bất động sản.
Khối ngoại bán ròng phiên thứ 6 liên tiếp với giá trị 337 tỷ đồng.
Phiên giảm điểm khiến điểm số kỹ thuật giảm từ mức -2 xuống -5 (TIÊU CỰC).

<Ví dụ 8: Thị trường tạo đỉnh mới>
Tiêu đề: Chạm đỉnh mới
VN-Index có phiên giao dịch đầy khởi sắc. Chỉ số đóng cửa ở mức cao mới, tăng 10,95 điểm (+0,82%). Thanh khoản cải thiện, khối lượng khớp lệnh đạt 890 triệu đơn vị, tương ứng giá trị giao dịch hơn 22.500 tỷ đồng.
Xét về độ rộng, thị trường nghiêng về số mã tăng. Nhóm chứng khoán là tâm điểm bứt phá.
Khối ngoại tạo điểm tích cực khi quay lại mua ròng 908 tỷ đồng.
Điểm số kỹ thuật cải thiện lên mức 3 (TRUNG TÍNH).

---
YÊU CẦU KHI VIẾT BÀI MỚI:
1.  **Tiêu đề:** Dựa vào "{expert_comment}" để đặt một tiêu đề giật tít (3-6 từ).
2.  **Cấu trúc 4 đoạn:**
    *   *Đoạn 1:* Diễn biến phiên, điểm số, thanh khoản (so sánh với phiên trước).
    *   *Đoạn 2:* **Độ rộng thị trường** (Phải nhận xét: "nghiêng về bên mua/bán" hoặc "cân bằng" dựa trên số mã Tăng/Giảm). Sau đó liệt kê Top tác động và Diễn biến ngành.
    *   *Đoạn 3:* Giao dịch Khối ngoại.
    *   *Đoạn 4:* Góc nhìn Kỹ thuật & P/E.
3.  **Ngôn ngữ:** Dùng từ chuyên ngành: "hệ sinh thái", "lực đỡ", "lao dốc", "ngược dòng", "thu hẹp đà giảm".

BẮT ĐẦU VIẾT:
"""