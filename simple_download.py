import os
import re
import requests
import time

# Cấu hình
INPUT_FILE = "source.txt"
OUTPUT_FOLDER = "data_pdfs"

# --- CẤU HÌNH GIẢ LẬP BRAVE TRÊN WINDOWS 11 ---
HEADERS = {
    # Đây là User-Agent chuẩn của Brave/Chrome mới nhất trên Windows 11
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://masvn.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Sec-Ch-Ua": '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Upgrade-Insecure-Requests": "1"
}

def main():
    # 1. Tạo thư mục lưu
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # 2. Đọc nội dung HTML
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Không thấy file '{INPUT_FILE}'. Hãy tạo nó và dán HTML vào.")
        return

    # 3. Tìm link PDF
    urls = re.findall(r'href="(https://[^"]+?\.pdf)"', content)
    urls = list(set(urls))

    print(f"🔍 Tìm thấy {len(urls)} link PDF. Bắt đầu tải...")

    # 4. Tải từng file
    for i, url in enumerate(urls):
        filename = url.split("/")[-1]
        filepath = os.path.join(OUTPUT_FOLDER, filename)

        if os.path.exists(filepath):
            # Kiểm tra xem file cũ có phải là file lỗi (HTML) không
            # Nếu file nhỏ hơn 1KB thì khả năng cao là file lỗi -> Tải lại
            if os.path.getsize(filepath) < 1024:
                print(f"[{i+1}/{len(urls)}] ⚠️ File cũ bị lỗi, tải lại: {filename}...")
            else:
                print(f"[{i+1}/{len(urls)}] ⏩ Đã có: {filename}")
                continue

        print(f"[{i+1}/{len(urls)}] ⬇️ Đang tải: {filename}...")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            
            if response.status_code == 200:
                # Kiểm tra kỹ xem có phải PDF thật không
                if b"%PDF" in response.content[:20]: 
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"   ✅ Tải thành công.")
                else:
                    print(f"   ❌ Vẫn bị chặn (Nội dung là HTML).")
            else:
                print(f"   ❌ Lỗi server: {response.status_code}")
                
            time.sleep(2) # Nghỉ 2 giây cho chắc ăn
            
        except Exception as e:
            print(f"   ❌ Lỗi kết nối: {e}")

    print(f"\n✅ HOÀN TẤT! File nằm trong thư mục '{OUTPUT_FOLDER}'")

if __name__ == "__main__":
    main()