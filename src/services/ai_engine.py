# File: src/services/ai_engine.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.models import DailyReportInput
from src.config import REPORT_PROMPT_TEMPLATE

load_dotenv()

class AIEngine:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️ Cảnh báo: Chưa có GOOGLE_API_KEY trong .env")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            # Dùng bản Flash cho nhanh và Context rộng
            self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_report(self, data: DailyReportInput) -> str:
        if not self.model:
            return "Lỗi: Chưa cấu hình API Key."

        # 1. Fill dữ liệu vào Prompt
        # LƯU Ý: Phải truyền ĐỦ tất cả các biến có trong ngoặc nhọn {} của config.py
        try:
            prompt = REPORT_PROMPT_TEMPLATE.format(
                date=data.date,
                vnindex_point=data.index.point,
                vnindex_change=data.index.change_point,
                vnindex_percent=data.index.change_percent,
                liquidity_value=f"{data.index.total_value:,.2f}",
                liquidity_comment=data.liquidity_comment,
                
                # Độ rộng thị trường
                breadth_green=data.index.breadth.green + data.index.breadth.ceiling, # Cộng cả trần
                breadth_red=data.index.breadth.red + data.index.breadth.floor,       # Cộng cả sàn
                breadth_yellow=data.index.breadth.yellow, # <--- MỚI THÊM
                
                # Khối ngoại
                foreign_status=data.foreign.status,
                foreign_value=data.foreign.net_value,
                foreign_buy_top=", ".join(data.foreign.top_buy),
                foreign_sell_top=", ".join(data.foreign.top_sell),
                
                # Tác động & Ngành
                impact_positive=", ".join(data.impact_positive),
                impact_negative=", ".join(data.impact_negative),
                sector_performance="\n".join([f"- {s.name}: {s.status} (Mã: {', '.join(s.top_gainers)})" for s in data.sectors]),
                
                # Chuyên gia
                technical_score=data.technical_score,
                technical_rating=data.technical_rating,
                pe_ratio=data.pe_ratio,
                expert_comment=data.expert_comment
            )
        except KeyError as e:
            return f"Lỗi Code: Thiếu biến {e} trong ai_engine.py so với config.py"

        # 2. Gọi Gemini
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Lỗi khi gọi Gemini: {str(e)}"