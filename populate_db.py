import sqlite3
from datetime import datetime, timedelta
import random

# Kullanıcı isimleri
user_names = ["Ali", "Ayşe", "Mehmet", "Zeynep", "Burak"]

# Lokasyonlar
locations = ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"]

# Veritabanına bağlan
conn = sqlite3.connect("anomaly_detection.db")
cursor = conn.cursor()

# Kullanıcıları ekle
for i, name in enumerate(user_names, start=1):
    registration_date = datetime.now() - timedelta(days=random.randint(100, 1000))
    cursor.execute("INSERT OR IGNORE INTO users (user_id, name, registration_date) VALUES (?, ?, ?)",
                   (i, name, registration_date.strftime("%Y-%m-%d")))

# İşlem verisi ekle
for user_id in range(1, len(user_names)+1):
    for _ in range(10):  # Her kullanıcıya 10 işlem
        amount = round(random.uniform(10, 1000), 2)
        txn_time = datetime.now() - timedelta(hours=random.randint(1, 240))
        location = random.choice(locations)
        is_anomaly = 0  # şimdilik hepsi normal
        cursor.execute("""
            INSERT INTO transactions (user_id, amount, txn_time, location, is_anomaly)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, amount, txn_time.strftime("%Y-%m-%d %H:%M:%S"), location, is_anomaly))

conn.commit()
conn.close()

print("✅ Sahte kullanıcı ve işlem verileri başarıyla eklendi.")
