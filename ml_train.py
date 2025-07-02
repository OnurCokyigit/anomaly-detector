# ================================
# 📥 1. GEREKLİ KÜTÜPHANELER
# ================================
import sqlite3
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

# ================================
# 🧠 2. VERİYİ VERİTABANINDAN ÇEK
# ================================
conn = sqlite3.connect("anomaly_detection.db")
df = pd.read_sql_query("SELECT * FROM transactions", conn)
conn.close()

# ================================
# 🕒 3. ZAMAN SÜTUNUNDAN SAATİ AYIKLA
# ================================
df["txn_time"] = pd.to_datetime(df["txn_time"])
df["hour"] = df["txn_time"].dt.hour

# ================================
# 🧹 4. KULLANILACAK SÜTUNLARI SEÇ
# ================================
df = df[[
    "user_id", "amount", "hour", "location", "transaction_type",
    "device_type", "channel", "browser_info", "os_type", "session_duration", "is_anomaly"
]]

# ================================
# 🔢 5. LABEL ENCODING (Kategorikleri Sayıya Çevir)
# ================================
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

# ================================
# 🧪 6. GİRİŞ / HEDEF AYIRIMI
# ================================
X = df[[
    "user_id", "amount", "hour", "location", "transaction_type",
    "device_type", "channel", "browser_info", "os_type", "session_duration"
]]
y = df["is_anomaly"]

# ================================
# 🔀 7. EĞİTİM / TEST AYRIMI
# ================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ================================
# 🎯 8. MODELİ EĞİT
# ================================
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ================================
# 📊 9. TEST SONUCU DEĞERLENDİR
# ================================
y_pred = model.predict(X_test)
report = classification_report(y_test, y_pred)
print("🔍 Model Performansı:\n")
print(report)

# ================================
# 💾 10. MODEL VE ENCODER'LARI KAYDET
# ================================
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/anomaly_model.pkl")
joblib.dump(label_user, "model/label_user.pkl")
joblib.dump(label_location, "model/label_location.pkl")
joblib.dump(label_transaction_type, "model/label_transaction_type.pkl")
joblib.dump(label_device_type, "model/label_device_type.pkl")
joblib.dump(label_channel, "model/label_channel.pkl")
joblib.dump(label_browser, "model/label_browser.pkl")
joblib.dump(label_os, "model/label_os.pkl")

# ================================
# 📝 11. PERFORMANS RAPORUNU KAYDET
# ================================
with open("model/performance_report.txt", "w") as f:
    f.write(report)

# ================================
# 📈 12. ÖZELLİK ÖNEMİNİ GRAFİĞE DÖK
# ================================
feature_names = [
    "user_id", "amount", "hour", "location", "transaction_type",
    "device_type", "channel", "browser_info", "os_type", "session_duration"
]
importances = model.feature_importances_

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importances
}).sort_values(by="importance", ascending=False)

# CSV olarak kaydet
importance_df.to_csv("model/feature_importance.csv", index=False)

# (İsteğe bağlı) PNG görseli olarak kaydet
plt.figure(figsize=(6, 4))
plt.barh(importance_df["feature"], importance_df["importance"], color="skyblue")
plt.gca().invert_yaxis()
plt.title("Feature Importance")
plt.tight_layout()
plt.savefig("model/feature_importance.png")

# ================================
# ✅ TAMAMLANDI
# ================================
print("✅ Model ve encoder'lar başarıyla kaydedildi → model klasörü")
print("📄 Performans raporu: model/performance_report.txt")
print("📊 Özellik önemi: model/feature_importance.csv ve .png")