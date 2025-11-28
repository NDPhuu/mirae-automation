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
            self.model = genai.GenerativeModel('gemini-pro')

    def generate_report(self, data: DailyReportInput) -> str:
        """
        Gửi dữ liệu sang Gemini để viết bài.
        """
        if not self.model:
            return "Lỗi: Chưa cấu hình API Key cho AI."

        # 1. Điền dữ liệu vào Prompt Template
        # Chuyển các list thành chuỗi văn bản (VD: ["A", "B"] -> "A, B")
        prompt = REPORT_PROMPT_TEMPLATE.format(
            vnindex_point=data.index.point,
            vnindex_change=data.index.change_point,
            vnindex_percent=data.index.change_percent,
            liquidity_value=f"{data.index.total_value/1_000_000_000:,.0f}",
            liquidity_comment=data.liquidity_comment,
            breadth_green=data.index.breadth.green,
            breadth_red=data.index.breadth.red,
            foreign_status=data.foreign.status,
            foreign_value=data.foreign.net_value,
            foreign_buy_top=", ".join(data.foreign.top_buy),
            foreign_sell_top=", ".join(data.foreign.top_sell),
            impact_positive=", ".join(data.impact_positive),
            impact_negative=", ".join(data.impact_negative),
            sector_performance="\n".join([f"- {s.name}: {s.status} (Mã: {', '.join(s.top_gainers)})" for s in data.sectors]),
            technical_score=data.technical_score,
            technical_rating=data.technical_rating,
            pe_ratio=data.pe_ratio,
            expert_comment=data.expert_comment
        )

        # 2. Gọi AI
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Lỗi khi gọi AI: {str(e)}"