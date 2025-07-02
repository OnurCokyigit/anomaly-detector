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
        cursor.execute(f"ALTER TABLE transactions ADD COLUMN {col} {dtype}")
        print(f"✅ '{col}' sütunu eklendi.")
    except:
        print(f"🔁 '{col}' sütunu zaten mevcut.")

conn.commit()
conn.close()
