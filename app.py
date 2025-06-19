import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from insert_and_detect import insert_transaction


def get_user_ids():
    conn = sqlite3.connect("anomaly_detection.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return user_ids


def get_location_list():
    return ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"]


def load_user_data(user_id):
    conn = sqlite3.connect("anomaly_detection.db")
    df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    return df


def main():
    st.set_page_config(page_title="Anomali Tespiti", layout="wide")
    st.title("📊 Anomali Tespiti Sistemi")

    tab1, tab2, tab3 = st.tabs(["➕ İşlem Ekle", "📈 Grafiksel Analiz", "🚨 Anomaliler"])

    with tab1:
        st.header("Yeni İşlem Ekle")
        user_ids = get_user_ids()
        user_id = st.selectbox("Kullanıcı Seç", user_ids)
        amount = st.number_input("İşlem Tutarı (TL)", min_value=1.0, step=1.0)
        location = st.selectbox("Lokasyon Seç", get_location_list())

        date = st.date_input("İşlem Tarihi", datetime.now().date())
        time = st.time_input("İşlem Saati", datetime.now().time())
        txn_time = datetime.combine(date, time)
        txn_time_str = txn_time.strftime("%Y-%m-%d %H:%M:%S")

        if st.button("💾 İşlemi Kaydet"):
            result = insert_transaction(user_id, amount, txn_time_str, location)
            if result is None:
                st.warning("⚠️ Bu işlem zaten kayıtlı.")
            elif result == 1:
                st.error("❗ Anomali tespit edildi ve işlem kaydedildi.")
            else:
                st.success("✅ İşlem normal ve başarıyla kaydedildi.")

    with tab2:
        st.header("Kullanıcı Bazlı Görselleştirme")
        user_ids = get_user_ids()
        selected_user = st.selectbox("Grafik için kullanıcı seç", user_ids, key="viz_user")
        df = load_user_data(selected_user)

        if df.empty:
            st.warning("Bu kullanıcıya ait işlem verisi yok.")
        else:
            st.subheader("📊 Özet Metrikler")
            total_txns = len(df)
            anomaly_count = df['is_anomaly'].sum()
            anomaly_rate = (anomaly_count / total_txns) * 100
            avg_amount = df['amount'].mean()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📦 Toplam İşlem", total_txns)
            col2.metric("⚠️ Anomali Sayısı", anomaly_count)
            col3.metric("📉 Anomali Oranı", f"{anomaly_rate:.1f}%")
            col4.metric("💸 Ortalama Tutar", f"{avg_amount:.2f} TL")

            st.subheader("📌 Anomali Dağılımı")
            counts = df["is_anomaly"].value_counts().rename({0: "Normal", 1: "Anomali"})
            st.bar_chart(counts)

            st.subheader("🕒 Saat Dağılımı")
            df["txn_time"] = pd.to_datetime(df["txn_time"])
            df["hour"] = df["txn_time"].dt.hour
            st.bar_chart(df["hour"].value_counts().sort_index())

    with tab3:
        st.header("🚨 Anomali İşlemleri")
        user_ids = get_user_ids()
        selected_user = st.selectbox("Anomali görüntüleme için kullanıcı seç", user_ids, key="anomaly_user")
        df = load_user_data(selected_user)

        if df.empty or df['is_anomaly'].sum() == 0:
            st.info("Bu kullanıcıya ait anomali işlemi bulunmamaktadır.")
        else:
            df_anomalies = df[df["is_anomaly"] == 1].copy()
            df_anomalies["txn_time"] = pd.to_datetime(df_anomalies["txn_time"])
            df_anomalies = df_anomalies.sort_values("txn_time", ascending=False)

            st.subheader(f"🔎 {selected_user} Kullanıcısına Ait {len(df_anomalies)} Anomali İşlem")

            st.dataframe(df_anomalies[["txn_time", "amount", "location"]])

            st.download_button(
                label="📥 Anomalileri İndir (CSV)",
                data=df_anomalies.to_csv(index=False).encode("utf-8"),
                file_name=f"user_{selected_user}_anomalies.csv",
                mime="text/csv"
            )

            st.markdown("---")
            st.bar_chart(df_anomalies.set_index("txn_time")["amount"])
            st.caption("🟠 Zaman serisine göre anomali tutarlarının dağılımı")


if __name__ == "__main__":
    main()
