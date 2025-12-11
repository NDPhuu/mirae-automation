# File: src/services/rag_service.py
import os
import glob
import shutil
import time
# Thay đổi thư viện import
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

class RAGService:
    def __init__(self, data_dir="data_clean_txt", db_dir="chroma_db"):
        self.data_dir = data_dir
        self.db_dir = db_dir
        self.vector_db = None # Chưa kết nối vội
        
        print("📥 Đang tải Model BGE-M3 (Chạy trên CPU)...")
        # Cấu hình chạy CPU
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-m3",
            model_kwargs={'device': 'cpu'}, 
            encode_kwargs={'normalize_embeddings': True}
        )

    def _get_db(self):
        """Hàm phụ trợ: Chỉ kết nối DB khi thực sự cần"""
        if self.vector_db is None:
            self.vector_db = Chroma(
                persist_directory=self.db_dir, 
                embedding_function=self.embeddings
            )
        return self.vector_db

    def ingest_data(self):
        """
        Hàm nạp dữ liệu.
        """
        # 1. Xử lý xóa DB cũ (Lúc này chưa kết nối nên xóa thoải mái)
        if os.path.exists(self.db_dir):
            print("🗑️ Phát hiện DB cũ, đang xóa...")
            try:
                shutil.rmtree(self.db_dir)
                time.sleep(1) # Nghỉ 1 xíu cho Windows kịp nhả file
                print("   -> Đã xóa xong.")
            except Exception as e:
                print(f"⚠️ Không xóa được folder cũ (Có thể do đang mở): {e}")
                print("👉 Hãy tắt các terminal khác hoặc xóa tay folder 'chroma_db' rồi chạy lại.")
                return

        # 2. Quét file
        print("🔄 Đang quét file dữ liệu...")
        files = glob.glob(f"{self.data_dir}/*.txt")
        
        if not files:
            print("❌ Không tìm thấy file .txt nào!")
            return

        documents = []
        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if len(content.strip()) < 10: continue
                    doc = Document(page_content=content, metadata={"source": file_path})
                    documents.append(doc)
            except Exception as e:
                print(f"⚠️ Lỗi đọc file {file_path}: {e}")

        if not documents:
            print("❌ Không có dữ liệu hợp lệ.")
            return

        print(f"🚀 Đang Vector hóa {len(documents)} tài liệu bằng GPU (RTX 3050)...")
        
        # 3. Bây giờ mới khởi tạo DB mới và nạp dữ liệu
        # Batch size lớn hơn chút vì có GPU
        batch_size = 50 
        
        # Khởi tạo Chroma mới
        temp_db = Chroma(
            persist_directory=self.db_dir, 
            embedding_function=self.embeddings
        )
        
        total_docs = len(documents)
        for i in range(0, total_docs, batch_size):
            batch = documents[i:i+batch_size]
            temp_db.add_documents(batch)
            print(f"   -> Đã xử lý {min(i + batch_size, total_docs)}/{total_docs} file...")

        print("✅ Đã nạp xong dữ liệu vào RAG Local!")
        self.vector_db = temp_db # Lưu lại kết nối

    def retrieve_similar_reports(self, query: str, k=5) -> str:
        """
        Tìm k bài báo cáo cũ giống với ngữ cảnh hiện tại nhất.
        """
        print(f"🔍 Đang tìm kiếm bài mẫu cho: {query}...")
        try:
            # Gọi hàm _get_db để đảm bảo đã kết nối
            db = self._get_db()
            results = db.similarity_search(query, k=k)
            
            context_text = ""
            for i, doc in enumerate(results):
                source = doc.metadata.get("source", "Unknown")
                # Chỉ lấy tên file cho gọn
                source_name = os.path.basename(source)
                context_text += f"\n--- BÀI MẪU {i+1} ({source_name}) ---\n{doc.page_content}\n"
                
            return context_text
        except Exception as e:
            return f"Lỗi tìm kiếm RAG: {str(e)}"

# --- CHẠY THỬ ---
if __name__ == "__main__":
    rag = RAGService()
    rag.ingest_data()