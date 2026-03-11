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
from src.services.data_aggregator import DataAggregator
from src.services.market_logic import MarketLogic
from src.services.ai_engine import AIEngine
from src.config import SECTOR_MAPPING

st.set_page_config(page_title="Mirae Asset Report Automation", layout="wide")

# --- HELPER FUNCTIONS ---
def load_data():
    all_symbols = []
    for symbols in SECTOR_MAPPING.values():
        all_symbols.extend(symbols)
    all_symbols = list(set(all_symbols))

    aggregator = DataAggregator()
    index_data, stocks_dict = aggregator.fetch_market_data(all_symbols)
    
    if index_data and stocks_dict:
        logic = MarketLogic()
        report_input = logic.prepare_report_input(index_data, stocks_dict)
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
    from src.cache import db
    
    col_btn, col_info = st.columns([1, 4])
    with col_info:
        # Lấy thời gian cập nhật gần nhất từ DB
        index_row = db.get_market_index("VNINDEX")
        if index_row and "updated_at" in index_row:
            try:
                # Đổi ISO string ra format dễ nhìn
                from datetime import datetime
                dt = datetime.fromisoformat(index_row["updated_at"])
                st.caption(f"🕒 Dữ liệu Cache cập nhật lúc: **{dt.strftime('%H:%M:%S - %d/%m/%Y')}** (Nhanh, không cần chờ API)")
            except:
                st.caption("🕒 Dữ liệu Cache: Đã có sẵn")
        else:
            st.warning("⚠️ Cache trống. Hãy chạy Market Streamer Daemon (src/workers/market_streamer.py) ở Background!")

    with col_btn:
        if st.button("⚡ TẢI TỪ CACHE (INSTANT)", type="primary"):
            data = load_data()
            if data:
                st.session_state.report_data = data
                st.success("Tải xong trong 0.05s!")
            else:
                st.error("Không tải được dữ liệu, Cache rỗng.")

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
            sector_rows = []
            for s in data.sectors:
                # Logic thông minh:
                # - Nếu ngành Tăng (avg_change > 0): Hiện mã Tăng (top_gainers)
                # - Nếu ngành Giảm (avg_change < 0): Hiện mã Giảm (top_losers)
                # - Nếu không có mã Tăng/Giảm tương ứng thì lấy mã còn lại
                
                if s.avg_change >= 0:
                    # Ưu tiên hiện mã tăng, nếu không có thì hiện mã giảm
                    stocks_show = s.top_gainers if s.top_gainers else s.top_losers
                else:
                    # Ưu tiên hiện mã giảm, nếu không có thì hiện mã tăng
                    stocks_show = s.top_losers if s.top_losers else s.top_gainers
                
                sector_rows.append({
                    "Ngành": s.name, 
                    "Trạng thái": s.status, 
                    "% TB": f"{s.avg_change:+.2f}%", # Thêm dấu +/- cho đẹp
                    "Mã Tiêu biểu": ", ".join(stocks_show)
                })

            sector_df = pd.DataFrame(sector_rows)
            st.dataframe(sector_df, hide_index=True, width='stretch')
            # --------------------

            # --- SECTION 3: KHỐI NGOẠI ---
            st.subheader("3. Giao dịch Khối ngoại (Manual Overrides Allowed)")
            c_f1, c_f2 = st.columns([1, 2])
            
            with c_f1:
                # Allow user to override net value
                st.write("**Trạng thái (Total Net Trading)**")
                data.foreign.status = st.selectbox("Hướng giao dịch:", ["MUA RÒNG", "BÁN RÒNG"], index=0 if data.foreign.status == "MUA RÒNG" else 1)
                data.foreign.net_value = st.number_input("Giá trị Net (Tỷ đồng):", value=float(data.foreign.net_value), step=10.0)
                
            with c_f2:
                # Convert the comma-separated strings back to editable text areas
                # so the user can easily format or change individual stocks and their values
                top_buy_str = ", ".join(data.foreign.top_buy)
                top_sell_str = ", ".join(data.foreign.top_sell)
                
                new_top_buy = st.text_input("Top Mua (Định dạng: HPG (+500 tỷ), FPT (+200 tỷ)): ", value=top_buy_str)
                new_top_sell = st.text_input("Top Bán (Định dạng: VCB (-500 tỷ), VIC (-200 tỷ)): ", value=top_sell_str)
                
                # Re-assign back to data object
                data.foreign.top_buy = [x.strip() for x in new_top_buy.split(",") if x.strip()]
                data.foreign.top_sell = [x.strip() for x in new_top_sell.split(",") if x.strip()]

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