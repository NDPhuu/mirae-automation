# File: src/ui/dashboard.py

import sys
import os

# Lấy đường dẫn tuyệt đối của file dashboard.py hiện tại
current_dir = os.path.dirname(os.path.abspath(__file__))
# Đi ngược lên 2 cấp để tìm về thư mục gốc dự án (mirae-automation)
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
# Thêm thư mục gốc vào danh sách tìm kiếm module của Python
sys.path.append(root_dir)


import streamlit as st
import pandas as pd
from src.services.dnse_service import DNSEService
from src.services.market_logic import MarketLogic
from src.services.ai_engine import AIEngine
from src.config import SECTOR_MAPPING

# Cấu hình trang
st.set_page_config(page_title="Mirae Asset Report Automation", layout="wide")


# --- HELPER FUNCTIONS ---
def load_data():
    """Hàm gọi Service lấy dữ liệu"""
    with st.spinner('Đang kết nối DNSE lấy dữ liệu thị trường...'):
        # 1. Lấy list mã
        all_symbols = []
        for symbols in SECTOR_MAPPING.values():
            all_symbols.extend(symbols)
        all_symbols = list(set(all_symbols))

        # 2. Gọi API
        service = DNSEService()
        raw_data = service.fetch_all_data(all_symbols)
        
        if raw_data and raw_data.get("index"):
            # 3. Gọi Logic
            logic = MarketLogic()
            report_input = logic.prepare_report_input(raw_data)
            return report_input
        return None

# --- MAIN UI ---
def main():
    st.title("📈 Mirae Asset Daily Report Assistant")
    st.markdown("---")

    # KHỞI TẠO SESSION STATE (Để lưu dữ liệu không bị mất khi reload)
    if 'report_data' not in st.session_state:
        st.session_state.report_data = None
    if 'generated_text' not in st.session_state:
        st.session_state.generated_text = ""

    # 1. NÚT LẤY DỮ LIỆU
    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        if st.button("🔄 LẤY DỮ LIỆU MỚI", type="primary"):
            data = load_data()
            if data:
                st.session_state.report_data = data
                st.success("Đã lấy dữ liệu thành công!")
            else:
                st.error("Không lấy được dữ liệu. Kiểm tra lại kết nối/API.")

    # HIỂN THỊ FORM NHẬP LIỆU (Chỉ hiện khi đã có data)
    if st.session_state.report_data:
        data = st.session_state.report_data
        
        with st.form("report_form"):
            st.subheader("1. Tổng quan thị trường (Market Overview)")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("VN-Index", f"{data.index.point}", f"{data.index.change_point:+.2f} ({data.index.change_percent:+.2f}%)")
            with c2:
                if data.index.total_value > 1_000_000_000:
                    val_ty = data.index.total_value / 1_000_000_000
                    st.metric("Thanh khoản", f"{val_ty:,.0f} Tỷ")
                else:
                    st.metric("Thanh khoản", f"{data.index.total_value:,.2f} Triệu")
            with c3:
                total_green = data.index.breadth.green + data.index.breadth.ceiling
                total_red = data.index.breadth.red + data.index.breadth.floor
                
                # Hiển thị chi tiết trong tooltip
                tooltip = f"Tăng: {data.index.breadth.green} (Trần {data.index.breadth.ceiling}) \nGiảm: {data.index.breadth.red} (Sàn {data.index.breadth.floor})"
                st.metric("Độ rộng", f"🟢{total_green} / 🔴{total_red}", help=tooltip)

            # Input chỉnh sửa nhận định thanh khoản
            data.liquidity_comment = st.text_input("Nhận xét Thanh khoản:", value="Thấp hơn trung bình 20 phiên")

            st.markdown("---")
            st.subheader("2. Diễn biến chi tiết")
            
            # Top Tác động
            c_imp1, c_imp2 = st.columns(2)
            with c_imp1:
                st.text_area("Top Tác động Tích cực (+)", value=", ".join(data.impact_positive), height=100)
            with c_imp2:
                st.text_area("Top Tác động Tiêu cực (-)", value=", ".join(data.impact_negative), height=100)

            # Nhóm ngành (Hiển thị dạng bảng cho dễ nhìn)
            st.write("📊 **Diễn biến Nhóm ngành (Máy tính toán):**")
            sector_df = pd.DataFrame([
                {"Ngành": s.name, "Trạng thái": s.status, "% TB": s.avg_change, "Mã Top": ", ".join(s.top_gainers)}
                for s in data.sectors
            ])
            st.dataframe(sector_df, hide_index=True)

            st.markdown("---")
            st.subheader("3. Dữ liệu Chuyên gia (Human Input)")
            
            c_exp1, c_exp2, c_exp3 = st.columns(3)
            with c_exp1:
                data.technical_score = st.number_input("Điểm Kỹ thuật (-7 đến +7):", min_value=-7, max_value=7, value=6)
            with c_exp2:
                data.technical_rating = st.selectbox("Đánh giá:", ["TÍCH CỰC", "KHẢ QUAN", "TRUNG TÍNH", "TIÊU CỰC"], index=1)
            with c_exp3:
                data.pe_ratio = st.number_input("P/E Thị trường:", value=15.5)

            data.expert_comment = st.text_area("Nhận định bổ sung (Key Highlight):", 
                                               value="Thị trường phân hóa mạnh, dòng tiền tìm đến nhóm cổ phiếu riêng lẻ.")

            # NÚT SUBMIT FORM & GỌI AI
            submitted = st.form_submit_button("✨ TẠO BÁO CÁO (GENERATE REPORT)")
            
            if submitted:
                with st.spinner("AI đang viết bài..."):
                    ai = AIEngine()
                    report_text = ai.generate_report(data)
                    st.session_state.generated_text = report_text

    # HIỂN THỊ KẾT QUẢ CUỐI CÙNG
    if st.session_state.generated_text:
        st.markdown("---")
        st.subheader("📝 Báo cáo Hoàn chỉnh (Draft)")
        final_report = st.text_area("Kết quả (Bạn có thể chỉnh sửa lần cuối ở đây):", 
                                    value=st.session_state.generated_text, 
                                    height=400)
        st.info("Copy nội dung trên và gửi đi!")

if __name__ == "__main__":
    main()