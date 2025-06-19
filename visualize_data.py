import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


def load_data_for_user(user_id):
    conn = sqlite3.connect("anomaly_detection.db")
    df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    return df


def plot_anomaly_distribution(df):
    counts = df['is_anomaly'].value_counts().rename({0: 'Normal', 1: 'Anomali'})
    counts.plot(kind='bar', color=['green', 'red'])
    plt.title("İşlem Türü Dağılımı")
    plt.ylabel("İşlem Sayısı")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()


def plot_time_distribution(df):
    df['txn_time'] = pd.to_datetime(df['txn_time'])
    df['hour'] = df['txn_time'].dt.hour
    df['hour'].value_counts().sort_index().plot(kind='bar')
    plt.title("İşlem Saatlerine Göre Dağılım")
    plt.xlabel("Saat")
    plt.ylabel("İşlem Sayısı")
    plt.tight_layout()
    plt.show()


def plot_amount_distribution(df):
    df['amount'].plot(kind='hist', bins=20, color='skyblue', edgecolor='black')
    plt.title("İşlem Tutarı Dağılımı")
    plt.xlabel("Tutar (TL)")
    plt.ylabel("Frekans")
    plt.tight_layout()
    plt.show()


def get_user_ids():
    conn = sqlite3.connect("anomaly_detection.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM transactions")
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return user_ids


def main():
    user_ids = get_user_ids()
    print(f"Mevcut kullanıcılar: {user_ids}")

    try:
        user_id = int(input("Grafik görmek istediğiniz kullanıcı ID'sini girin: "))
        if user_id not in user_ids:
            print("❌ Bu kullanıcıya ait işlem bulunamadı.")
            return

        df = load_data_for_user(user_id)

        if df.empty:
            print("❌ Bu kullanıcıya ait işlem kaydı yok.")
            return

        print(f"\n📈 Kullanıcı {user_id} için grafikler gösteriliyor...\n")
        plot_anomaly_distribution(df)
        plot_time_distribution(df)
        plot_amount_distribution(df)

    except Exception as e:
        print(f"⚠️ Hata: {e}")


if __name__ == "__main__":
    main()
