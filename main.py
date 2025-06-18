import sqlite3

# Veritabanına bağlan (dosya yoksa otomatik oluşturur)
conn = sqlite3.connect("anomaly_detection.db")
cursor = conn.cursor()

# users tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    registration_date TEXT
)
""")

# transactions tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    txn_time TEXT,
    location TEXT,
    is_anomaly INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

# Değişiklikleri kaydet ve bağlantıyı kapat
conn.commit()
conn.close()

print("✅ Veritabanı ve tablolar başarıyla oluşturuldu.")
