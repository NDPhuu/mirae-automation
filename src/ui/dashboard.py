# File: src/ui/dashboard.py
import sys
import os

# --- 1. FIX LỖI IMPORT ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.append(root_dir)
# -------------------------

import streamlit as st
import pandas as pd
from src.services.dnse_service import DNSEService
from src.services.market_logic import MarketLogic
from src.services.ai_engine import AIEngine
from src.config import SECTOR_MAPPING

st.set_page_config(page_title="Mirae Asset Report Automation", layout="wide")

# --- HELPER FUNCTIONS ---
def load_data():
    with st.spinner('Đang kết nối DNSE lấy dữ liệu thị trường...'):
        all_symbols = []
        for symbols in SECTOR_MAPPING.values():
            all_symbols.extend(symbols)
        all_symbols = list(set(all_symbols))

        service = DNSEService()
        raw_data = service.fetch_all_data(all_symbols)
        
        if raw_data and raw_data.get("index"):
            logic = MarketLogic()
            report_input = logic.prepare_report_input(raw_data)
            return report_input
        return None

# --- MAIN UI ---
def main():
    st.title("📈 Mirae Asset Daily Report Assistant")
    st.markdown("---")

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

    # 2. FORM NHẬP LIỆU & HIỂN THỊ
    if st.session_state.report_data:
        data = st.session_state.report_data
        
        with st.form("report_form"):
            # --- SECTION 1: TỔNG QUAN (CHIA 4 CỘT) ---
            st.subheader("1. Tổng quan thị trường (Market Overview)")
            
            # Thay đổi: Chia thành 4 cột để hiển thị Giá trị riêng
            c1, c2, c3, c4 = st.columns(4)
            
            # Cột 1: Điểm số
            with c1:
                change_str = f"{data.index.change_point:+.2f}"
                percent_str = f"{data.index.change_percent:.2f}%"
                st.metric("VN-Index", f"{data.index.point:.2f}", f"{change_str} ({percent_str})")
            
            # Cột 2: Khối lượng (Volume)
            with c2:
                vol_million = data.index.total_volume / 1_000_000
                st.metric("Khối lượng", f"{vol_million:,.2f} Tr CP")
                
            # Cột 3: Giá trị (Value) - QUAN TRỌNG
            with c3:
                val_billion = data.index.total_value
                val_str = "N/A" if val_billion == 0 else f"{val_billion:,.0f}"
                st.metric("Giá trị GD", f"{val_str} Tỷ", help="Tổng giá trị khớp lệnh + thỏa thuận sàn HSX")
            
            # Cột 4: Độ rộng
            with c4:
                total_green = data.index.breadth.green + data.index.breadth.ceiling
                total_red = data.index.breadth.red + data.index.breadth.floor
                tooltip = f"Tăng: {data.index.breadth.green} (Trần {data.index.breadth.ceiling}) \nGiảm: {data.index.breadth.red} (Sàn {data.index.breadth.floor})"
                st.metric("Độ rộng", f"🟢{total_green} / 🔴{total_red}", help=tooltip)

            data.liquidity_comment = st.text_input("Nhận xét Thanh khoản:", value="Thấp hơn trung bình 20 phiên")

            st.markdown("---")
            
            # --- SECTION 2: DIỄN BIẾN ---
            st.subheader("2. Diễn biến chi tiết")
            c_imp1, c_imp2 = st.columns(2)
            with c_imp1:
                st.text_area("Top Tác động Tích cực (+)", value=", ".join(data.impact_positive), height=100)
            with c_imp2:
                st.text_area("Top Tác động Tiêu cực (-)", value=", ".join(data.impact_negative), height=100)

            st.write("📊 **Diễn biến Nhóm ngành:**")
            sector_df = pd.DataFrame([
                {"Ngành": s.name, "Trạng thái": s.status, "% TB": s.avg_change, "Mã Top": ", ".join(s.top_gainers)}
                for s in data.sectors
            ])
            st.dataframe(sector_df, hide_index=True)

            st.markdown("---")

            # --- SECTION 3: KHỐI NGOẠI ---
            st.subheader("3. Giao dịch Khối ngoại")
            c_f1, c_f2 = st.columns([1, 2])
            with c_f1:
                st.metric(
                    label="Trạng thái", 
                    value=data.foreign.status, 
                    delta=f"{data.foreign.net_value:,.2f} Tỷ"
                )
            with c_f2:
                st.info(f"**Top Mua:** {', '.join(data.foreign.top_buy)}")
                st.warning(f"**Top Bán:** {', '.join(data.foreign.top_sell)}")

            st.markdown("---")

            # --- SECTION 4: CHUYÊN GIA ---
            st.subheader("4. Dữ liệu Chuyên gia (Human Input)")
            c_exp1, c_exp2, c_exp3 = st.columns(3)
            with c_exp1:
                data.technical_score = st.number_input("Điểm Kỹ thuật (-7 đến +7):", min_value=-7, max_value=7, value=6)
            with c_exp2:
                data.technical_rating = st.selectbox("Đánh giá:", ["TÍCH CỰC", "KHẢ QUAN", "TRUNG TÍNH", "TIÊU CỰC"], index=1)
            with c_exp3:
                data.pe_ratio = st.number_input("P/E Thị trường:", value=15.5)

            data.expert_comment = st.text_area("Nhận định bổ sung (Key Highlight):", 
                                               value="Thị trường phân hóa mạnh, dòng tiền tìm đến nhóm cổ phiếu riêng lẻ.")

            # NÚT SUBMIT
            submitted = st.form_submit_button("✨ TẠO BÁO CÁO (GENERATE REPORT)", type="primary")
            
            if submitted:
                with st.spinner("AI đang viết bài..."):
                    ai = AIEngine()
                    report_text = ai.generate_report(data)
                    st.session_state.generated_text = report_text

    # 3. HIỂN THỊ KẾT QUẢ
    if st.session_state.generated_text:
        st.markdown("---")
        st.subheader("📝 Báo cáo Hoàn chỉnh (Draft)")
        st.text_area("Kết quả:", value=st.session_state.generated_text, height=500)
        st.info("Copy nội dung trên và gửi đi!")

if __name__ == "__main__":
    main()