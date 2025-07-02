import sqlite3
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# --- Veritabanından veriyi oku ---
conn = sqlite3.connect("anomaly_detection.db")
df = pd.read_sql_query("SELECT * FROM transactions", conn)
conn.close()

# --- Tarih sütununu saat bilgisine dönüştür ---
df["txn_time"] = pd.to_datetime(df["txn_time"])
df["hour"] = df["txn_time"].dt.hour

# --- Gerekli öznitelikleri seç ---
df = df[[
    "user_id", "amount", "hour", "location", "transaction_type",
    "device_type", "channel", "browser_info", "os_type", "session_duration", "is_anomaly"
]]

# --- Kategorik sütunları sayısallaştır ---
label_user = LabelEncoder()
label_location = LabelEncoder()
label_transaction_type = LabelEncoder()
label_device_type = LabelEncoder()
label_channel = LabelEncoder()
label_browser = LabelEncoder()
label_os = LabelEncoder()

df["user_id"] = label_user.fit_transform(df["user_id"])
df["location"] = label_location.fit_transform(df["location"])
df["transaction_type"] = label_transaction_type.fit_transform(df["transaction_type"].fillna("unknown"))
df["device_type"] = label_device_type.fit_transform(df["device_type"].fillna("unknown"))
df["channel"] = label_channel.fit_transform(df["channel"].fillna("unknown"))
df["browser_info"] = label_browser.fit_transform(df["browser_info"].fillna("unknown"))
df["os_type"] = label_os.fit_transform(df["os_type"].fillna("unknown"))

# --- Giriş (X) ve hedef (y) ayrımı ---
X = df[[
    "user_id", "amount", "hour", "location", "transaction_type",
    "device_type", "channel", "browser_info", "os_type", "session_duration"
]]
y = df["is_anomaly"]

# --- Kontrol için ilk 5 satırı göster ---
print("X veri örneği:")
print(X.head())
print("\nHedef etiket (y):")
print(y.value_counts())
