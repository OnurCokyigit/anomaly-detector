from datetime import datetime
from insert_and_detect import insert_transaction
import sqlite3

def get_user_ids():
    conn = sqlite3.connect("anomaly_detection.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return user_ids

def get_location_list():
    return ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"]

def main():
    print("=== İşlem Ekleme Arayüzü ===")

    user_ids = get_user_ids()
    print(f"Kayıtlı kullanıcılar: {user_ids}")

    try:
        user_id = int(input("Kullanıcı ID'si: "))
        if user_id not in user_ids:
            print("❌ Bu ID'ye sahip bir kullanıcı yok.")
            return

        amount = float(input("İşlem Tutarı (TL): "))
        location = input(f"Lokasyon ({', '.join(get_location_list())}): ")
        if location not in get_location_list():
            print("❌ Geçersiz lokasyon.")
            return

        txn_time_input = input("İşlem zamanı (YYYY-MM-DD HH:MM:SS) [Boş bırakılırsa şimdi]: ")
        if txn_time_input.strip() == "":
            txn_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            txn_time = datetime.strptime(txn_time_input, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

        transaction_type = input("İşlem Türü (ör. ödeme, transfer): ")
        device_type = input("Cihaz Türü (ör. Mobile, Desktop): ")
        channel = input("Kanal (ör. Web, App): ")
        browser_info = input("Tarayıcı Bilgisi (ör. Chrome): ")
        os_type = input("İşletim Sistemi (ör. Windows, Android): ")
        ip_address = input("IP Adresi: ")
        session_duration = float(input("Oturum Süresi (saniye): "))

    except Exception as e:
        print(f"⚠️ Hata: {e}")
        return

    result = insert_transaction(user_id, amount, txn_time, location,
                                transaction_type, device_type, channel,
                                browser_info, os_type, ip_address, session_duration)

    if result is None:
        print("❗ Aynı işlem zaten kayıtlı. Giriş iptal edildi.")
    elif result == 1:
        print("⚠️ Bu işlem ANOMALİ olarak işaretlendi.")
    else:
        print("✅ Bu işlem normal.")

if __name__ == "__main__":
    main()
