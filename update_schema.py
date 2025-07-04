import sqlite3

conn = sqlite3.connect("anomaly_detection.db")
cursor = conn.cursor()

columns = {
    "transaction_type": "TEXT",
    "device_type": "TEXT",
    "channel": "TEXT",
    "browser_info": "TEXT",
    "os_type": "TEXT",
    "ip_address": "TEXT",
    "session_duration": "REAL"
}

for col, dtype in columns.items():
    try:
        cursor.execute("ALTER TABLE transactions ADD COLUMN anomaly_score REAL")
    except:
        print("🔁 'anomaly_score' zaten mevcut.")
conn.commit()
conn.close()
