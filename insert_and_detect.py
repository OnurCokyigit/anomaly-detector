import sqlite3
from datetime import datetime
import joblib
import os
import subprocess
import sys
import pandas as pd
import requests

# --- Model ve encoder dosyaları ---
MODEL_PATH = "model/anomaly_model.pkl"
ENC_USER_PATH = "model/label_user.pkl"
ENC_LOC_PATH = "model/label_location.pkl"
ENC_TRANS_TYPE = "model/label_transaction_type.pkl"
ENC_DEVICE_TYPE = "model/label_device_type.pkl"
ENC_CHANNEL = "model/label_channel.pkl"
ENC_BROWSER = "model/label_browser_info.pkl"
ENC_OS = "model/label_os_type.pkl"

# --- Yüklemeye çalış ---
try:
    model = joblib.load(MODEL_PATH)
    label_user = joblib.load(ENC_USER_PATH)
    label_location = joblib.load(ENC_LOC_PATH)
    label_transaction_type = joblib.load(ENC_TRANS_TYPE)
    label_device_type = joblib.load(ENC_DEVICE_TYPE)
    label_channel = joblib.load(ENC_CHANNEL)
    label_browser_info = joblib.load(ENC_BROWSER)
    label_os_type = joblib.load(ENC_OS)
    print("✅ ML modeli ve encoder'lar yüklendi.")
except Exception as e:
    print(f"⚠️ Model veya encoder dosyaları yüklenemedi: {e}")
    model = None


# --- Telegrama bor aracılığı ile mesaj gönder ---
def send_telegram_alert(user_id, amount, location, anomaly_score):
    BOT_TOKEN = "7691631732:AAHcRucTL9vCZp1FovXNdm-nsNczvSRSEmc"
    CHAT_ID = "5630479338"

    message = f"""
🚨 <b>Anomali Tespit Edildi</b>
👤 <b>Kullanıcı:</b> {user_id}
💸 <b>Tutar:</b> {amount} TL
📍 <b>Lokasyon:</b> {location}
🧠 <b>Model Skoru:</b> {anomaly_score:.2f}
"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)


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

    hour = datetime.strptime(txn_time, "%Y-%m-%d %H:%M:%S").hour

    # 🌟 Özellik kodlamaları
    try:
        user_encoded = label_user.transform([user_id])[0] if user_id in label_user.classes_ else 0
        location_encoded = label_location.transform([location])[0] if location in label_location.classes_ else 0
        transaction_type_encoded = label_transaction_type.transform([transaction_type])[0] if transaction_type in label_transaction_type.classes_ else 0
        device_type_encoded = label_device_type.transform([device_type])[0] if device_type in label_device_type.classes_ else 0
        channel_encoded = label_channel.transform([channel])[0] if channel in label_channel.classes_ else 0
        browser_info_encoded = label_browser_info.transform([browser_info])[0] if browser_info in label_browser_info.classes_ else 0
        os_type_encoded = label_os_type.transform([os_type])[0] if os_type in label_os_type.classes_ else 0
    except Exception as e:
        print(f"⚠️ Özellik kodlama hatası: {e}")
        user_encoded = location_encoded = transaction_type_encoded = 0
        device_type_encoded = channel_encoded = browser_info_encoded = os_type_encoded = 0

    # 🧠 ML tahmini
    if model:
        try:
            features = pd.DataFrame([{
                "user_id": user_encoded,
                "amount": amount,
                "hour": hour,
                "location": location_encoded,
                "transaction_type": transaction_type_encoded,
                "device_type": device_type_encoded,
                "channel": channel_encoded,
                "browser_info": browser_info_encoded,
                "os_type": os_type_encoded,
                "session_duration": session_duration or 0
            }])
            proba = model.predict_proba(features)[0][1]  # 1: anomali olasılığı
            ml_score = int(proba >= 0.5)  # Eşik değer 0.5
            anomaly_score = round(proba, 4)
            print(f"🤖 ML Tahmini: {ml_score} | Anomali Skoru: {anomaly_score}")
        except Exception as e:
            print(f"⚠️ ML tahmin hatası: {e}")
            ml_score = 0
    else:
        print("ℹ️ Model yüklü değil.")
        ml_score = 0

    # ✅ Nihai Anomali Kararı
    if hour < 6 and amount > 1500:
        is_anomaly = 1  # Gece + yüksek tutar → kesin anomali
        print("🌙 Gece ve yüksek tutar → Anomali olarak işaretlendi.")
    else:
        is_anomaly = ml_score  # Diğer durumlarda ML kararına göre
        print(f"🔍 ML Kararıyla işaretlendi → Anomali: {is_anomaly}")

    # 🔽 Veriyi kaydet
    cursor.execute("""
        INSERT INTO transactions (
            user_id, amount, txn_time, location, is_anomaly,
            transaction_type, device_type, channel,
            browser_info, os_type, ip_address, session_duration,
            anomaly_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, amount, txn_time, location, is_anomaly,
        transaction_type, device_type, channel,
        browser_info, os_type, ip_address, session_duration,
        anomaly_score
    ))

    # 🧮 Risk skoru güncelle
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ? AND is_anomaly = 1", (user_id,))
    anomalies = cursor.fetchone()[0]
    score = int((anomalies / total) * 100) if total > 0 else 0
    cursor.execute("UPDATE users SET risk_score = ? WHERE user_id = ?", (score, user_id))

    conn.commit()

    # 🔄 Her 100 işlemde model eğit
    cursor.execute("SELECT COUNT(*) FROM transactions")
    txn_count = cursor.fetchone()[0]
    conn.close()

    if txn_count % 100 == 0:
        print(f"🔄 {txn_count} işlemde bir: Model yeniden eğitiliyor...")
        try:
            subprocess.run([sys.executable, "ml_train.py"], check=True)
            print("✅ Model yeniden eğitildi.")
        except Exception as e:
            print(f"❌ Model eğitimi hatası: {e}")

    if is_anomaly == 1:
        send_telegram_alert(user_id, amount, location, anomaly_score)

    return is_anomaly, anomaly_score
