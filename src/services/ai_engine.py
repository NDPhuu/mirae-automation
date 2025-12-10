# File: src/services/ai_engine.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.models import DailyReportInput
from src.services.rag_service import RAGService
from src.config import REPORT_PROMPT_TEMPLATE

load_dotenv()

class AIEngine:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️ Cảnh báo: Chưa có GOOGLE_API_KEY")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Khởi tạo RAG
        self.rag = RAGService()

    def _build_rich_query(self, data: DailyReportInput) -> str:
        """
        Biến số liệu thô thành một đoạn văn mô tả ngữ cảnh (Contextual Description).
        Mục tiêu: Giúp BGE-M3 hiểu được 'Cảm xúc thị trường' chứ không chỉ là con số.
        """
        # 1. Xác định Xu hướng (Trend Sentiment)
        change = data.index.change_percent
        if change >= 1.5: trend = "thị trường bùng nổ, tăng điểm mạnh mẽ, hưng phấn"
        elif change >= 0.5: trend = "thị trường tăng điểm tích cực, sắc xanh lan tỏa"
        elif change >= 0.0: trend = "thị trường hồi phục nhẹ, giằng co quanh tham chiếu"
        elif change >= -0.5: trend = "thị trường điều chỉnh nhẹ, áp lực chốt lời, rung lắc"
        elif change >= -1.5: trend = "thị trường giảm điểm, sắc đỏ chiếm ưu thế"
        else: trend = "thị trường giảm mạnh, bán tháo, hoảng loạn, thủng hỗ trợ"

        # 2. Xác định Thanh khoản (Liquidity Sentiment)
        # Giả định mốc trung bình là 15k tỷ (có thể chỉnh logic này thông minh hơn sau này)
        val = data.index.total_value / 1_000_000_000
        if val > 25000: liq = "thanh khoản bùng nổ kỷ lục, dòng tiền ồ ạt"
        elif val > 18000: liq = "thanh khoản ở mức cao, dòng tiền sôi động"
        elif val > 12000: liq = "thanh khoản trung bình"
        else: liq = "thanh khoản cạn kiệt, dòng tiền thận trọng, tiết cung"

        # 3. Xác định Khối ngoại
        foreign = f"khối ngoại {data.foreign.status.lower()} {data.foreign.net_value} tỷ"

        # 4. Ghép thành câu Query hoàn chỉnh
        # Cấu trúc: [Xu hướng] + [Thanh khoản] + [Khối ngoại] + [Nhận định chuyên gia]
        rich_query = (
            f"Báo cáo nhận định {trend}. "
            f"Diễn biến {liq}. "
            f"Giao dịch {foreign}. "
            f"Tâm lý thị trường: {data.expert_comment}"
        )
        
        print(f"🔍 RICH QUERY: {rich_query}") # In ra để debug xem nó tạo câu gì
        return rich_query

    def generate_report(self, data: DailyReportInput) -> str:
        if not self.model:
            return "Lỗi: Chưa cấu hình API Key."

        # 1. Tạo Rich Query (Thay vì query ngắn cũn)
        query = self._build_rich_query(data)
        
        # 2. Gọi RAG để tìm bài mẫu tương tự ngữ cảnh này
        rag_context = self.rag.retrieve_similar_reports(query, k=3)

        # 3. Fill dữ liệu vào Prompt
        try:
            prompt = REPORT_PROMPT_TEMPLATE.format(
                date=data.date,
                vnindex_point=data.index.point,
                vnindex_change=data.index.change_point,
                vnindex_percent=data.index.change_percent,
                liquidity_volume=f"{data.index.total_volume / 1_000_000:,.0f}",
                liquidity_value=f"{data.index.total_value:,.0f}",
                liquidity_comment=data.liquidity_comment,
                breadth_green=data.index.breadth.green + data.index.breadth.ceiling,
                breadth_red=data.index.breadth.red + data.index.breadth.floor,
                breadth_yellow=data.index.breadth.yellow,
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
                expert_comment=data.expert_comment,
                
                rag_context=rag_context # Nhồi bài mẫu tìm được vào
            )
        except KeyError as e:
            return f"Lỗi Code: Thiếu biến {e}"

        # 4. Gọi Gemini
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Lỗi khi gọi Gemini: {str(e)}"