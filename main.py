import sqlite3

conn = sqlite3.connect("anomaly_detection.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    registration_date TEXT
)
""")

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

conn.commit()
conn.close()

print("✅ Database and tables have been created successfully.")



