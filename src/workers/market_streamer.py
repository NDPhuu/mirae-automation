import os
import sys
import time
import json
import ssl
import random
import threading
import paho.mqtt.client as mqtt
import warnings
import urllib3
from datetime import datetime

# Tắt các cảnh báo không quan trọng từ thư viện bên thứ 3
warnings.filterwarnings("ignore", category=DeprecationWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add root dir to sys path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(root_dir)

from src.config import SECTOR_MAPPING
from src.services.dnse_service import DNSEService
from src.services.ssi_service import SSIService
from src.cache import db

def start_dnse_mqtt_stream(symbols_list):
    """Connects to DNSE MQTT and constantly pushes updates to SQLite."""
    print("🚀 Khởi động luồng DNSE MQTT Streamer...")
    dnse = DNSEService()
    if not dnse.login():
        print("❌ Lỗi đăng nhập DNSE. Streamer bị hủy.")
        return

    client_id = f"dnse-streamer-{dnse.investor_id}-{random.randint(1000, 9999)}"
    client = mqtt.Client(client_id=client_id, transport="websockets")
    client.username_pw_set(username=dnse.investor_id, password=dnse.token)
    client.tls_set_context(context=ssl.create_default_context())
    client.ws_set_options(path="/wss")

    def on_connect(c, userdata, flags, rc):
        if rc == 0:
            print(f"🔌 DNSE Connected. Đang đăng ký VNINDEX và {len(symbols_list)} mã cổ phiếu...")
            c.subscribe("plaintext/quotes/krx/mdds/index/VNINDEX")
            for symbol in symbols_list:
                c.subscribe(f"plaintext/quotes/krx/mdds/stockinfo/v1/roundlot/symbol/{symbol}")
        else:
            print(f"❌ DNSE Connection Failed: {rc}")

    def on_message(c, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            topic = msg.topic

            if "index/VNINDEX" in topic:
                db.upsert_index("VNINDEX", {
                    "point": payload.get("valueIndexes", 0.0),
                    "change_point": payload.get("changedValue", 0.0),
                    "change_percent": payload.get("changedRatio", 0.0),
                    "total_value": payload.get("grossTradeAmount", 0.0),
                    "total_volume": payload.get("totalVolumeTraded", 0.0),
                    "breadth_green": payload.get("fluctuationUpIssueCount", 0),
                    "breadth_red": payload.get("fluctuationDownIssueCount", 0),
                    "breadth_yellow": payload.get("fluctuationSteadinessIssueCount", 0),
                    "breadth_ceiling": payload.get("fluctuationUpperLimitIssueCount", 0),
                    "breadth_floor": payload.get("fluctuationLowerLimitIssueCount", 0)
                })
                # print("✅ VNINDEX updated in Cache")

            elif "stockinfo" in topic:
                symbol = payload.get("symbol")
                if symbol:
                    db.upsert_stock(symbol, {
                        "price": payload.get("closePrice", 0.0),
                        "ref_price": payload.get("referencePrice", 0.0),
                        "change_percent": payload.get("changedRatio", 0.0),
                        "volume": payload.get("totalVolumeTraded", 0)
                    })
                    # print(f"   -> {symbol} price updated")

        except Exception as e:
            print(f"⚠️ DNSE Stream Parse Error: {e}")

    def on_disconnect(client, userdata, rc):
        print(f"⚠️ DNSE Ngắt kết nối (Mã {rc}). Sẽ tự kết nối lại tự động...")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Enable automatic reconnect with exponential backoff
    client.reconnect_delay_set(min_delay=1, max_delay=60)

    try:
        client.connect(dnse.MQTT_HOST, dnse.MQTT_PORT, 60)
        # Bật vòng lặp vĩnh viễn trong thread nội bộ của Paho
        client.loop_start()
        return client
    except Exception as e:
        print(f"❌ Lỗi khởi động MQTT: {e}")
        return None

class SSIConfig:
    def __init__(self):
        import os
        from dotenv import load_dotenv
        load_dotenv()
        self.consumerID = os.getenv("SSI_CONSUMER_ID")
        self.consumerSecret = os.getenv("SSI_CONSUMER_SECRET")
        # ssi_fc_data SDK already appends 'api/v2/...' to requests.
        # So we MUST strictly pass the root domain here.
        env_url = os.getenv("SSI_FC_URL", "https://fc-data.ssi.com.vn/")
        if "api/v2" in env_url:
            env_url = env_url.split("api/v2")[0]
        if not env_url.endswith("/"):
            env_url += "/"
        self.url = env_url
        
        self.stream_url = "https://fc-datahub.ssi.com.vn/"
        self.auth_type = "Bearer"

def start_ssi_signalr_stream():
    """Uses SignalR via ssi_fc_data to stream real-time Foreign trading data."""
    from ssi_fc_data.fc_md_client import MarketDataClient
    from ssi_fc_data.fc_md_stream import MarketDataStream
    
    config = SSIConfig()
    if not config.consumerID or not config.consumerSecret:
        print("❌ Lỗi cấu hình SSI_CONSUMER_ID. Streamer bị hủy.")
        return
        
    print("🚀 Khởi động SSI SignalR Streamer...")
    client = MarketDataClient(config)
    stream = MarketDataStream(config, client)

    def on_message(message):
        try:
            # message is JSON string
            import json
            data = json.loads(message)
            if data.get("DataType") == "R":  # Foreign Room datatype is 'R'
                content = data.get("Content", "")
                if isinstance(content, str):
                    content = json.loads(content)
                    
                symbol = content.get("Symbol")
                buy_val = float(content.get("BuyVal", 0.0))
                sell_val = float(content.get("SellVal", 0.0))
                
                if symbol and (buy_val > 0 or sell_val > 0):
                    db.upsert_stock(symbol, {
                        "f_buy_val": buy_val,
                        "f_sell_val": sell_val
                    })
        except Exception as e:
            pass # Ignore parsing errors on noisy stream
            
    def on_error(error):
        print(f"⚠️ SSI Stream Lỗi: {error}")

    try:
        # Start matching the official documentation style: 'R:ALL'
        stream.start(on_message, on_error, "R:ALL")
    except Exception as e:
        print(f"❌ Khởi tạo SSI Stream thất bại: {e}")

def initial_seed_data(symbols_list):
    """
    Fetches the static EOD state from DNSE & SSI ONCE at startup to populate SQLite.
    This guarantees data is fully available for formatting even if the stream is quiet (e.g. weekends).
    """
    print("⏳ Đang tải dữ liệu tĩnh (Lịch sử) lần đầu để nạp Cache...")
    
    # 1. Quét DNSE lấy giá, volume, shares, VNINDEX (FAST - DONE IN SECONDS)
    dnse = DNSEService()
    base_data = dnse.fetch_all_data(symbols_list)
    if base_data:
        # Lưu VNINDEX
        idx = base_data.get("index")
        if idx:
            db.upsert_index("VNINDEX", {
                "point": idx.point,
                "change_point": idx.change_point,
                "change_percent": idx.change_percent,
                "total_value": idx.total_value,
                "total_volume": idx.total_volume,
                "breadth_green": idx.breadth.green,
                "breadth_red": idx.breadth.red,
                "breadth_yellow": idx.breadth.yellow,
                "breadth_ceiling": idx.breadth.ceiling,
                "breadth_floor": idx.breadth.floor
            })
            
        # Lưu các mã cổ phiếu
        stocks = base_data.get("stocks", {})
        for sym, s_data in stocks.items():
            db.upsert_stock(sym, {
                "price": s_data.get("price", 0.0),
                "ref_price": s_data.get("ref_price", 0.0),
                "change_percent": s_data.get("change_percent", 0.0),
                "shares": s_data.get("listed_shares", 0),
                "volume": s_data.get("volume", 0)
            })
        print(f"✅ [DNSE] Đã tải xong nền tảng (Giá, Khối lượng) cho {len(stocks)} mã.")

    # 2. ListedShare Data (Số CP niêm yết cho Top Impact) - (FAST - FROM JSON)
    # Tìm file JSON ở path tuyệt đối để đảm bảo không sai lệch do Working Directory
    cache_path = os.path.join(root_dir, "data", "listed_shares_cache.json")
    print(f"🔍 [CACHE] Đang tìm kiếm ListedShare tại: {cache_path}")
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding='utf-8') as f:
                cache_data = json.load(f)
                shares_map = cache_data.get("shares", {})
                
                count = 0
                for sym, shares in shares_map.items():
                    if shares > 0:
                        db.upsert_stock(sym, {"shares": shares})
                        count += 1
                print(f"✅ [CACHE] Đã nạp xong ListedShare cho {count}/{len(shares_map)} mã từ JSON.")
        except Exception as e:
            print(f"⚠️ [CACHE] Lỗi nạp dữ liệu từ JSON: {e}")
    else:
        print(f"❌ [CACHE] KHÔNG TÌM THẤY FILE: {cache_path}. Top Impact sẽ bị trống!")

    # 3. Quét SSI lấy Foreign Trading + SEC Details (OPTIMIZED)
    def ssi_background_fetch():
        now = datetime.now()
        # SKIP: Nếu đang trong giờ giao dịch và đã có dữ liệu cache (EOD SSI không đổi trong ngày)
        # Chỉ Force-run nếu là sáng sớm (1h-8h) hoặc sau phiên (16h-23h)
        is_trading_hours = 9 <= now.hour < 16
        
        print(f"⏳ [SSI] Bắt đầu kiểm tra Dữ liệu Khối ngoại (Time: {now.strftime('%H:%M')})...")
        
        ssi = SSIService()
        if ssi.login():
            # Tối ưu: Lấy danh sách mã ưu tiên (VN30 + High Impact)
            # Giả định VN30 + mã cốt lõi (~50 mã)
            vn30 = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIC","VJC","VNM","VPB","VRE"]
            
            # Phase 1: Tier 1 (VN30 - Instant update)
            print("🚀 [SSI] Tier 1: Ưu tiên VN30...")
            f_data_tier1 = ssi.get_batch_foreign_data(vn30)
            for sym, d in f_data_tier1.items():
                db.upsert_stock(sym, {
                    "f_buy_val": d.get('f_buy_val', 0.0),
                    "f_sell_val": d.get('f_sell_val', 0.0)
                }, trading_date=d.get("trading_date"))
            
            # Phase 2: Tier 2 (Phần còn lại - Skip nếu đang trong giờ giao dịch)
            if is_trading_hours:
                print("⏭️ [SSI] Đang giờ giao dịch, bỏ qua Tier 2 để tiết kiệm tài nguyên (Dùng Cache).")
                return

            print("⏳ [SSI] Tier 2: Đang tải nốt phần còn lại của thị trường...")
            remaining_symbols = [s for s in symbols_list if s not in vn30]
            f_data_tier2 = ssi.get_batch_foreign_data(remaining_symbols)
            for sym, d in f_data_tier2.items():
                db.upsert_stock(sym, {
                    "f_buy_val": d.get('f_buy_val', 0.0),
                    "f_sell_val": d.get('f_sell_val', 0.0)
                }, trading_date=d.get("trading_date"))
            
            print(f"✅ [SSI] Đã hoàn thành cập nhật Khối ngoại toàn thị trường.")
            
    # Chạy SSI fetch trong thread riêng để không block streamer startup
    threading.Thread(target=ssi_background_fetch, daemon=True).start()

def start_streams():
    print("========================================")
    print("    MIRAE MARKET STREAMER DAEMON        ")
    print("========================================")
    
    all_symbols = []
    for symbols in SECTOR_MAPPING.values():
        all_symbols.extend(symbols)
    all_symbols = list(set(all_symbols))
    
    # 1. Db Init (Starts Flusher thread)
    db.init_db()
    
    # 2. Seed data (First run)
    initial_seed_data(all_symbols)
    
    # 3. Start streams
    mqtt_client = start_dnse_mqtt_stream(all_symbols)
    
    ssi_thread = threading.Thread(target=start_ssi_signalr_stream, daemon=True)
    ssi_thread.start()
    
    return mqtt_client

def main():
    mqtt_client = start_streams()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Đang tắt Streamer Daemon...")
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
        db.stop_flusher()
        sys.exit(0)

if __name__ == "__main__":
    main()
