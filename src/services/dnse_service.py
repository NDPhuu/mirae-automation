# File: src/services/dnse_service.py
import json
import os
import ssl
import random
import time
import requests
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from typing import List, Dict, Any
from src.models import MarketIndex, MarketBreadth

load_dotenv()

class DNSEService:
    def __init__(self):
        self.username = os.getenv("DNSE_USERNAME")
        self.password = os.getenv("DNSE_PASSWORD")
        self.token = None
        self.investor_id = None
        
        # Endpoint Config
        self.AUTH_URL = "https://api.dnse.com.vn/user-service/api/auth"
        self.USER_INFO_URL = "https://api.dnse.com.vn/user-service/api/me"
        self.MQTT_HOST = "datafeed-lts-krx.dnse.com.vn"
        self.MQTT_PORT = 443
        
        # Nơi chứa dữ liệu tạm thời khi đang hứng từ MQTT
        self._temp_data = {
            "index": None,
            "stocks": {} # Dạng {"HPG": {...data...}, "VCB": {...}}
        }

    def login(self):
        """Đăng nhập lấy Token"""
        try:
            res = requests.post(self.AUTH_URL, json={"username": self.username, "password": self.password})
            if res.status_code != 200:
                print(f"❌ Login Failed: {res.text}")
                return False
            self.token = res.json().get("token")
            
            headers = {"Authorization": f"Bearer {self.token}"}
            res_me = requests.get(self.USER_INFO_URL, headers=headers)
            self.investor_id = res_me.json().get("investorId")
            return True
        except Exception as e:
            print(f"❌ Login Error: {e}")
            return False

    def fetch_all_data(self, stock_list: List[str]) -> Dict[str, Any]:
        """
        Hàm quan trọng nhất: Lấy cả VNINDEX và Danh sách cổ phiếu cùng lúc.
        Input: stock_list = ["HPG", "VCB", "SSI"...]
        Output: Dictionary chứa toàn bộ dữ liệu thô.
        """
        if not self.token and not self.login():
            return None

        # Reset kho chứa
        self._temp_data = {"index": None, "stocks": {}}
        
        # Setup MQTT
        random_seq = str(random.randint(1000, 9999))
        client_id = f"dnse-batch-{self.investor_id}-{random_seq}"
        client = mqtt.Client(client_id=client_id, transport="websockets")
        client.username_pw_set(username=self.investor_id, password=self.token)
        client.tls_set_context(context=ssl.create_default_context())
        client.ws_set_options(path="/wss")

        def on_connect(c, userdata, flags, rc):
            if rc == 0:
                print(f"[DNSE REST] Connected. Subscribing to Index + {len(stock_list)} Stocks...")
                # 1. Sub VNINDEX
                c.subscribe("plaintext/quotes/krx/mdds/index/VNINDEX")
                
                # 2. Sub từng mã cổ phiếu (Topic Stock Info)
                # Topic format: plaintext/quotes/krx/mdds/stockinfo/v1/roundlot/symbol/{SYMBOL}
                for symbol in stock_list:
                    topic = f"plaintext/quotes/krx/mdds/stockinfo/v1/roundlot/symbol/{symbol}"
                    c.subscribe(topic)
            else:
                print(f"❌ Connection Failed: {rc}")

        def on_message(c, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
                topic = msg.topic

                # A. Xử lý VNINDEX
                if "index/VNINDEX" in topic:
                    # Map vào Model ngay lập tức cho gọn
                    breadth = MarketBreadth(
                        green=payload.get("fluctuationUpIssueCount", 0),
                        red=payload.get("fluctuationDownIssueCount", 0),
                        yellow=payload.get("fluctuationSteadinessIssueCount", 0),
                        ceiling=payload.get("fluctuationUpperLimitIssueCount", 0),
                        floor=payload.get("fluctuationLowerLimitIssueCount", 0)
                    )
                    self._temp_data["index"] = MarketIndex(
                        symbol="VNINDEX",
                        point=payload.get("valueIndexes"),
                        change_point=payload.get("changedValue"),
                        change_percent=payload.get("changedRatio"),
                        total_value=payload.get("grossTradeAmount"),
                        total_volume=payload.get("totalVolumeTraded", 0),
                        breadth=breadth
                    )
                    # print("Got VN-Index")

                # B. Xử lý Cổ phiếu lẻ
                elif "stockinfo" in topic:
                    symbol = payload.get("symbol")
                    if symbol:
                        self._temp_data["stocks"][symbol] = {
                            "price": payload.get("closePrice"),
                            "ref_price": payload.get("referencePrice"), # Giá tham chiếu
                            "change_percent": payload.get("changedRatio", 0.0),
                            "volume": payload.get("totalVolumeTraded", 0),
                            "f_buy_val": payload.get("buyForeignValue", 0.0),  # Giá trị Tây mua
                            "f_sell_val": payload.get("sellForeignValue", 0.0), # Giá trị Tây bán
                            "listed_shares": payload.get("listedShares", 0) # Số cổ phiếu đăng ký
                        }
                        # print(f"   -> Got {symbol}") # Uncomment nếu muốn debug chi tiết

            except Exception as e:
                print(f"⚠️ Parse Error: {e}")

        client.on_connect = on_connect
        client.on_message = on_message

        # Chạy vòng lặp chờ dữ liệu
        try:
            client.connect(self.MQTT_HOST, self.MQTT_PORT, 60)
            client.loop_start()
            
            # Cơ chế chờ thông minh (Timeout 15s)
            # Chờ đến khi lấy được Index VÀ ít nhất 90% số cổ phiếu yêu cầu
            max_retries = 30 # 30 * 0.5s = 15s
            for _ in range(max_retries):
                got_index = self._temp_data["index"] is not None
                got_stocks_count = len(self._temp_data["stocks"])
                
                # Nếu đã lấy được Index và > 90% danh sách cổ phiếu thì dừng sớm
                # if got_index and got_stocks_count >= len(stock_list) * 0.9:
                #     print("🚀 Đã lấy đủ dữ liệu cần thiết.")
                #     break
    
                time.sleep(1)
                
            client.loop_stop()
            client.disconnect()
            return self._temp_data
            
        except Exception as e:
            print(f"❌ MQTT Error: {e}")
            return None