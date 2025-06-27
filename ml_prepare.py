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
df = df[["user_id", "amount", "hour", "location", "is_anomaly"]]

# --- Kategorik sütunları sayısallaştır ---
label_user = LabelEncoder()
label_location = LabelEncoder()

df["user_id"] = label_user.fit_transform(df["user_id"])
df["location"] = label_location.fit_transform(df["location"])

# --- Giriş (X) ve hedef (y) ayrımı ---
X = df[["user_id", "amount", "hour", "location"]]
y = df["is_anomaly"]

# --- Kontrol için ilk 5 satırı göster ---
print("X veri örneği:")
print(X.head())
print("\nHedef etiket (y):")
print(y.value_counts())
