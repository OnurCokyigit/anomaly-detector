import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

# --- Veritabanından veri çek ---
conn = sqlite3.connect("anomaly_detection.db")
df = pd.read_sql_query("SELECT * FROM transactions", conn)
conn.close()

# --- Saat sütununu çıkar ---
df["txn_time"] = pd.to_datetime(df["txn_time"])
df["hour"] = df["txn_time"].dt.hour

# --- Kullanılacak sütunlar ---
df = df[["user_id", "amount", "hour", "location", "is_anomaly"]]

# --- Kategorikleri sayıya çevir ---
label_user = LabelEncoder()
label_location = LabelEncoder()

df["user_id"] = label_user.fit_transform(df["user_id"])
df["location"] = label_location.fit_transform(df["location"])

# --- Giriş ve hedef ayrımı ---
X = df[["user_id", "amount", "hour", "location"]]
y = df["is_anomaly"]

# --- Eğitim/test ayır ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Modeli eğit ---
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# --- Test verisi üzerinde değerlendir ---
y_pred = model.predict(X_test)
report = classification_report(y_test, y_pred)
print("🔍 Model Performansı:\n")
print(report)

# --- Klasör oluştur ---
os.makedirs("model", exist_ok=True)

# --- Model ve encoder'ları kaydet ---
joblib.dump(model, "model/anomaly_model.pkl")
joblib.dump(label_user, "model/label_user.pkl")
joblib.dump(label_location, "model/label_location.pkl")

# --- Performans raporunu kaydet ---
with open("model/performance_report.txt", "w") as f:
    f.write(report)

print("✅ Model ve encoder'lar başarıyla kaydedildi → model klasörü")
print("📄 Performans raporu: model/performance_report.txt")
