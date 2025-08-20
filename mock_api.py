from fastapi import FastAPI
from datetime import datetime
import random
app = FastAPI()

user_ids = [1, 2, 3, 4, 5]
locations = ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"]
transaction_types = ["odeme", "transfer", "cekme"]
device_types = ["Mobile", "Desktop"]
channels = ["Web", "App"]
browsers = ["Chrome", "Firefox", "Safari"]
os_list = ["Windows", "iOS", "Android"]
ip_pool = ["192.168.1.1", "10.0.0.2", "172.16.0.3"]

@app.get("/transaction")
def get_transaction():
    transaction = {
        "user_id": random.choice(user_ids),
        "amount": round(random.uniform(10, 2000), 2),
        "location": random.choice(locations),
        "txn_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "transaction_type": random.choice(transaction_types),
        "device_type": random.choice(device_types),
        "channel": random.choice(channels),
        "browser_info": random.choice(browsers),
        "os_type": random.choice(os_list),
        "ip_address": random.choice(ip_pool),
        "session_duration": round(random.uniform(5, 600), 2)
    }
    return transaction




