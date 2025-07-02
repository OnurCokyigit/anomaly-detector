import sqlite3
from datetime import datetime
import joblib
import os
import subprocess
import sys
import pandas as pd

# --- Model ve encoder dosyaları ---
MODEL_PATH = "model/anomaly_model.pkl"
ENC_USER_PATH = "model/label_user.pkl"
ENC_LOC_PATH = "model/label_location.pkl"

# --- Yüklemeye çalış ---
try:
    model = joblib.load(MODEL_PATH)
    label_user = joblib.load(ENC_USER_PATH)
    label_location = joblib.load(ENC_LOC_PATH)
    print("✅ ML modeli ve encoder'lar yüklendi.")
except Exception as e:
    print(f"⚠️ Model veya encoder dosyaları yüklenemedi: {e}")
    model = None
    label_user = None
    label_location = None

# --- Yeni işlem veritabanına kaydeder ---
def insert_transaction(user_id, amount, txn_time, location,
                       transaction_type=None, device_type=None, channel=None,
                       browser_info=None, os_type=None, ip_address=None, session_duration=None):
    conn = sqlite3.connect("anomaly_detection.db")
    cursor = conn.cursor()

    # 🔁 Aynı işlem zaten var mı?
    cursor.execute("""
        SELECT COUNT(*) FROM transactions
        WHERE user_id = ? AND amount = ? AND txn_time = ? AND location = ?
    """, (user_id, amount, txn_time, location))
    if cursor.fetchone()[0] > 0:
        print("⚠️ Bu işlem zaten kayıtlı.")
        conn.close()
        return None

    # 🌟 ML tahmini yap
    if model and label_user and label_location:
        try:
            hour = datetime.strptime(txn_time, "%Y-%m-%d %H:%M:%S").hour

            if user_id in label_user.classes_:
                user_encoded = label_user.transform([user_id])[0]
            else:
                print(f"⚠️ Yeni kullanıcı ID: {user_id} (daha önce görülmemiş)")
                user_encoded = 0

            if location in label_location.classes_:
                location_encoded = label_location.transform([location])[0]
            else:
                print(f"⚠️ Yeni lokasyon: {location} (daha önce görülmemiş)")
                location_encoded = 0

            features = pd.DataFrame([{
                "user_id": user_encoded,
                "amount": amount,
                "hour": hour,
                "location": location_encoded
            }])
            prediction = model.predict(features)[0]
            is_anomaly = int(prediction)
            print(f"🤖 ML Tahmini: {is_anomaly}")
        except Exception as e:
            print(f"⚠️ ML tahmin hatası: {e}")
            is_anomaly = 0
    else:
        print("ℹ️ Model/encoder eksik. Anomali kontrolü yapılmadı.")
        is_anomaly = 0

    # Veriyi kaydet
    cursor.execute("""
        INSERT INTO transactions (
            user_id, amount, txn_time, location, is_anomaly,
            transaction_type, device_type, channel,
            browser_info, os_type, ip_address, session_duration
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, amount, txn_time, location, is_anomaly,
        transaction_type, device_type, channel,
        browser_info, os_type, ip_address, session_duration
    ))
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM transactions")
    txn_count = cursor.fetchone()[0]
    conn.close()

    if txn_count % 100 == 0:
        print(f"🔄 Toplam işlem sayısı: {txn_count}. Model yeniden eğitiliyor...")
        try:
            subprocess.run([sys.executable, "ml_train.py"], check=True)
            print("✅ Model yeniden eğitildi.")
        except Exception as e:
            print(f"❌ Model eğitimi sırasında hata: {e}")

    return is_anomaly
