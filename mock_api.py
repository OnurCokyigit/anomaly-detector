from fastapi import FastAPI
from datetime import datetime
import random

app = FastAPI()

# Sahte veri için parametre havuzu
user_ids = [1, 2, 3, 4, 5]
locations = ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"]

@app.get("/transaction")
def get_transaction():
    transaction = {
        "user_id": random.choice(user_ids),
        "amount": round(random.uniform(10, 2000), 2),
        "location": random.choice(locations),
        "txn_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return transaction
