import pdfplumber
import os
import re
from pathlib import Path

# --- CẤU HÌNH ---
INPUT_FOLDER = "data_pdfs"       # Thư mục chứa 180 file PDF của bạn
OUTPUT_FOLDER = "data_clean_txt" # Thư mục chứa file Text kết quả

def clean_text(text):
    """Làm sạch văn bản: Xóa dòng thừa, header, footer"""
    if not text:
        return ""
    
    lines = text.split('\n')
    cleaned_lines = []
    
    # Các từ khóa cần loại bỏ (Noise)
    noise_keywords = [
        "Bản tin cuối ngày", "Mirae Asset", "cs@miraeasset.com.vn", 
        "Trang", "Page", "Disclaimer", "Khuyến cáo", "Nguồn:", 
        "Tổng quan thị trường", "Định giá thị trường"
    ]
    
    for line in lines:
        line = line.strip()
        # 1. Bỏ dòng rỗng
        if not line: 
            continue
        # 2. Bỏ dòng quá ngắn (số trang, rác)
        if len(line) < 5: 
            continue
        # 3. Bỏ các dòng chứa từ khóa nhiễu
        if any(keyword.lower() in line.lower() for keyword in noise_keywords):
            continue
        # 4. Bỏ các dòng giống dòng kẻ bảng (chứa quá nhiều số)
        # Nếu số lượng chữ số > 50% độ dài dòng -> Khả năng cao là số liệu bảng
        digit_count = sum(c.isdigit() for c in line)
        if digit_count > len(line) * 0.5:
            continue
            
        cleaned_lines.append(line)
        
    return "\n".join(cleaned_lines)

def extract_mirae_report(pdf_path):
    full_content = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # --- XỬ LÝ TRANG 1: NHẬN ĐỊNH THỊ TRƯỜNG ---
        # Layout Mirae: Cột trái là số, Cột phải là chữ.
        # Ta sẽ crop lấy 60% bên phải trang giấy.
        p1 = pdf.pages[0]
        width = p1.width
        height = p1.height
        
        # Crop box: (x0, top, x1, bottom)
        # Lấy từ 40% chiều rộng đổ đi (bỏ cột trái)
        p1_right_col = p1.crop((width * 0.4, 50, width, height - 50))
        text_p1 = p1_right_col.extract_text()
        
        full_content.append("## 1. NHẬN ĐỊNH THỊ TRƯỜNG")
        full_content.append(clean_text(text_p1))
        
        # --- XỬ LÝ TRANG 2: PHÂN TÍCH KỸ THUẬT ---
        # Thường nằm ở 40% phía trên trang
        if len(pdf.pages) > 1:
            p2 = pdf.pages[1]
            p2_top = p2.crop((0, 50, width, height * 0.4)) # Lấy 40% trên cùng
            text_p2 = p2_top.extract_text()
            full_content.append("\n## 2. PHÂN TÍCH KỸ THUẬT")
            full_content.append(clean_text(text_p2))

        # --- XỬ LÝ TRANG 3: PHÁI SINH ---
        if len(pdf.pages) > 2:
            p3 = pdf.pages[2]
            p3_top = p3.crop((0, 50, width, height * 0.4))
            text_p3 = p3_top.extract_text()
            full_content.append("\n## 3. PHÁI SINH")
            full_content.append(clean_text(text_p3))
            
        # --- XỬ LÝ TIN TỨC (Thường từ trang 6-7 trở đi) ---
        # Phần này khó fix cứng, ta lấy text thô và lọc kỹ
        if len(pdf.pages) >= 7:
            full_content.append("\n## 4. TIN TỨC VĨ MÔ")
            for i in range(6, min(9, len(pdf.pages))): # Quét từ trang 7 đến 9
                page = pdf.pages[i]
                text_news = page.extract_text()
                full_content.append(clean_text(text_news))

    return "\n".join(full_content)

def main():
    # Tạo thư mục output nếu chưa có
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    
    # Lấy danh sách file PDF
    pdf_files = list(Path(INPUT_FOLDER).glob("*.pdf"))
    print(f"📂 Tìm thấy {len(pdf_files)} file PDF.")
    
    for i, pdf_file in enumerate(pdf_files):
        print(f"[{i+1}/{len(pdf_files)}] Đang xử lý: {pdf_file.name}...")
        try:
            # Trích xuất
            content = extract_mirae_report(pdf_file)
            
            # Lưu ra file txt
            output_filename = pdf_file.stem + ".txt"
            output_path = Path(OUTPUT_FOLDER) / output_filename
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# BÁO CÁO GỐC: {pdf_file.name}\n\n")
                f.write(content)
                
        except Exception as e:
            print(f"❌ Lỗi file {pdf_file.name}: {e}")

    print("\n✅ HOÀN TẤT! Kiểm tra thư mục:", OUTPUT_FOLDER)

if __name__ == "__main__":
    main()