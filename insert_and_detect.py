import sqlite3
from datetime import datetime

# --- Kullanıcının alışkanlık profilini çıkarır ---
def get_user_profile(user_id):
    conn = sqlite3.connect("anomaly_detection.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT amount, txn_time, location FROM transactions
        WHERE user_id = ?
        ORDER BY txn_time DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None  # Yeterli veri yok

    amounts = [row[0] for row in rows]
    times = [datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S") for row in rows]
    locations = [row[2] for row in rows]

    # Ortalama ve standart sapma
    avg_amount = sum(amounts) / len(amounts)
    std_amount = (sum((x - avg_amount)**2 for x in amounts) / len(amounts))**0.5

    # En sık lokasyon
    most_common_location = max(set(locations), key=locations.count)

    # En sık saat
    hours = [t.hour for t in times]
    most_common_hour = max(set(hours), key=hours.count)

    return {
        "avg_amount": avg_amount,
        "std_amount": std_amount,
        "location": most_common_location,
        "hour": most_common_hour
    }

# --- Profil bazlı anomali kontrolü ---
def is_anomalous(txn, profile):
    if profile is None:
        print("ℹ️ Profil bulunamadı, ilk işlemler olabilir. Anomali sayılmayacak.")
        return False

    amount = txn["amount"]
    txn_time = datetime.strptime(txn["txn_time"], "%Y-%m-%d %H:%M:%S")
    hour = txn_time.hour
    location = txn["location"]

    flags = 0

    print("\n--- Anomali Analizi ---")
    print(f"💰 Kullanıcının ortalama tutarı: {profile['avg_amount']:.2f}")
    print(f"📈 Std sapma: {profile['std_amount']:.2f}")
    print(f"📊 Gelen işlem tutarı: {amount}")
    print(f"⏰ İşlem saati: {hour}, 👣 Lokasyon: {location}")
    print(f"🔍 Sapma: {abs(amount - profile['avg_amount']):.2f} TL, Eşik: {1.5 * profile['std_amount']:.2f}")

    # 1. Tutar kontrolü
    if abs(amount - profile["avg_amount"]) > 1.5 * profile["std_amount"]:
        print("⚠️ Tutar eşik dışında")
        flags += 1

    # 2. Lokasyon kontrolü
    if location != profile["location"]:
        print(f"⚠️ Lokasyon farkı ({profile['location']} yerine {location})")
        flags += 1

    # 3. Saat kontrolü
    if abs(hour - profile["hour"]) > 3:
        print(f"⚠️ Saat farkı ({profile['hour']} yerine {hour})")
        flags += 1

    print(f"🚩 Toplam ihlal sayısı: {flags}\n")
    return flags >= 2


# --- Yeni işlem veritabanına kaydeder ---
def insert_transaction(user_id, amount, txn_time, location):
    conn = sqlite3.connect("anomaly_detection.db")
    cursor = conn.cursor()

    # Aynı işlem daha önce eklenmiş mi?
    cursor.execute("""
        SELECT COUNT(*) FROM transactions
        WHERE user_id = ? AND amount = ? AND txn_time = ? AND location = ?
    """, (user_id, amount, txn_time, location))

    if cursor.fetchone()[0] > 0:
        print("⚠️ Bu işlem zaten kayıtlı. Yeniden eklenmeyecek.")
        conn.close()
        return None 

    txn = {
        "user_id": user_id,
        "amount": amount,
        "txn_time": txn_time,
        "location": location
    }

    profile = get_user_profile(user_id)
    is_anomaly = 1 if is_anomalous(txn, profile) else 0


    cursor.execute("""
        INSERT INTO transactions (user_id, amount, txn_time, location, is_anomaly)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, amount, txn_time, location, is_anomaly))
    conn.commit()
    conn.close()

    return is_anomaly  # işlem sonrası sonucu geri döner
