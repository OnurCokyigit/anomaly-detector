
import streamlit as st
import sqlite3
from insert_and_detect import insert_transaction
import pandas as pd
from datetime import datetime
import time
import requests

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

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ İşlem Ekle",
        "📈 Grafiksel Analiz",
        "🚨 Anomaliler",
        "📡 Canlı Veri Akışı",
        "🧠 Model Performansı"
    ])

    with tab1:
        st.header("Yeni İşlem Ekle")
        user_ids = get_user_ids()
        user_id = st.selectbox("Kullanıcı Seç", user_ids)
        amount = st.number_input("İşlem Tutarı (TL)", min_value=1.0, step=1.0)
        location = st.selectbox("Lokasyon Seç", get_location_list())

        date = st.date_input("İşlem Tarihi", datetime.now().date())
        txn_time_input = st.time_input("İşlem Saati", datetime.now().time())
        txn_time = datetime.combine(date, txn_time_input)
        txn_time_str = txn_time.strftime("%Y-%m-%d %H:%M:%S")

        if st.button("💾 İşlemi Kaydet"):
            result = insert_transaction(user_id, amount, txn_time_str, location)
            if result is None:
                st.markdown("""
                    <div style='background-color:#fff3cd; padding:10px; border-radius:10px;'>
                        ⚠️ Bu işlem zaten kayıtlı.
                    </div>
                """, unsafe_allow_html=True)
            elif result == 1:
                st.markdown("""
                    <div style='background-color:#f8d7da; padding:10px; border-radius:10px;'>
                        ❗ Anomali tespit edildi ve işlem kaydedildi.
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style='background-color:#d4edda; padding:10px; border-radius:10px;'>
                        ✅ İşlem normal ve başarıyla kaydedildi.
                    </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.header("Kullanıcı Bazlı Görselleştirme")
        user_ids = get_user_ids()
        selected_user = st.selectbox("Grafik için kullanıcı seç", user_ids, key="viz_user")
        df = load_user_data(selected_user)

        if df.empty:
            st.markdown("""
                <div style='background-color:#fff3cd; padding:10px; border-radius:10px;'>
                    Bu kullanıcıya ait işlem verisi yok.
                </div>
            """, unsafe_allow_html=True)
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
            st.markdown("""
                            <div style='background-color:#d1ecf1; padding:10px; border-radius:10px;'>
                                Bu kullanıcıya ait anomali işlemi bulunmamaktadır.
                            </div>
                        """, unsafe_allow_html=True)
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

    # with tab4:
    #     st.header("📡 Canlı Veri Akışı (API Tabanlı)")
    #     start = st.button("🔄 Veriyi Çek ve Kaydet")
    #
    #     if start:
    #         try:
    #             response = requests.get("http://127.0.0.1:8000/transaction")
    #             if response.status_code == 200:
    #                 data = response.json()
    #                 st.write("📥 Alınan Veri:", data)
    #
    #                 # Veriyi DB'ye kaydet ve anomali kontrolü yap
    #                 result = insert_transaction(
    #                     user_id=data["user_id"],
    #                     amount=data["amount"],
    #                     txn_time=data["txn_time"],
    #                     location=data["location"]
    #                 )
    #
    #                 if result == 1:
    #                     st.error("🚨 Anomali Tespit Edildi!")
    #                 else:
    #                     st.success("✅ İşlem Normal")
    #
    #             else:
    #                 st.warning(f"Sunucudan beklenmedik yanıt: {response.status_code}")
    #
    #         except Exception as e:
    #             st.error(f"⚠️ Hata: {e}")

    with tab4:
        st.header("📡 Canlı Veri Akışı (API Tabanlı)")
        st.markdown("Bu sekmede API üzerinden veri alımı yapabilirsiniz.")

        mode = st.radio("Veri alma modu seçin:", ["🔁 Otomatik Akış", "🔢 Sayı Girerek Alım"], horizontal=True)

        if "stop_stream" not in st.session_state:
            st.session_state["stop_stream"] = False

        status_box = st.empty()
        result_box = st.empty()

        def handle_result(data, index=None, total=None):
            txn_info = f"📥 Yeni Veri Alındı"
            if index is not None and total is not None:
                txn_info += f" ({index}/{total})"

            status_box.markdown(f"""
                <div style="background-color:#f0f2f6; padding:10px; border-radius:10px">
                    <b>{txn_info}:</b><br>
                    👤 <b>Kullanıcı ID:</b> {data['user_id']}<br>
                    💸 <b>Tutar:</b> {data['amount']} TL<br>
                    🗺️ <b>Lokasyon:</b> {data['location']}<br>
                    ⏰ <b>Zaman:</b> {data['txn_time']}
                </div>
            """, unsafe_allow_html=True)

            result = insert_transaction(
                user_id=data["user_id"],
                amount=data["amount"],
                txn_time=data["txn_time"],
                location=data["location"]
            )

            if result == 1:
                result_box.markdown("""
                    <div style='background-color:#f8d7da; padding:10px; border-radius:10px;'>
                        🚨 Anomali tespit edildi!
                    </div>
                """, unsafe_allow_html=True)
            else:
                result_box.markdown("""
                    <div style='background-color:#d4edda; padding:10px; border-radius:10px;'>
                        ✅ İşlem normal.
                    </div>
                """, unsafe_allow_html=True)

        # --- Otomatik Akış Modu ---
        if mode == "🔁 Otomatik Akış":
            start_button = st.button("▶️ Otomatik Akışı Başlat")
            stop_button = st.button("⛔ Durdur")

            if stop_button:
                st.session_state["stop_stream"] = True

            if start_button:
                st.session_state["stop_stream"] = False
                status_box.info("📡 Otomatik veri akışı başladı...")
                while not st.session_state["stop_stream"]:
                    try:
                        response = requests.get("http://127.0.0.1:8000/transaction")
                        if response.status_code == 200:
                            data = response.json()
                            handle_result(data)
                        else:
                            status_box.warning(f"⚠️ Beklenmedik yanıt: {response.status_code}")
                    except Exception as e:
                        result_box.error(f"⚠️ Hata: {e}")

                    time.sleep(5)

        # --- Sayı Girerek Veri Alımı ---
        if mode == "🔢 Sayı Girerek Alım":
            num_requests = st.number_input("📦 Kaç işlem alınsın?", min_value=1, max_value=100, value=5)
            start_fixed = st.button("▶️ Belirli Sayıda Al", key="start_fixed")
            stop_fixed = st.button("⛔ Durdur", key="stop_fixed")

            if stop_fixed:
                st.session_state["stop_stream"] = True

            if start_fixed:
                st.session_state["stop_stream"] = False
                status_box.info("🔢 Belirli sayıda veri alımı başladı...")

                for i in range(int(num_requests)):
                    if st.session_state["stop_stream"]:
                        status_box.warning("⛔ Veri alımı durduruldu.")
                        break

                    try:
                        response = requests.get("http://127.0.0.1:8000/transaction")
                        if response.status_code == 200:
                            data = response.json()
                            handle_result(data, i + 1, num_requests)
                        else:
                            status_box.warning(f"⚠️ Beklenmedik yanıt: {response.status_code}")
                    except Exception as e:
                        result_box.error(f"⚠️ Hata: {e}")

                    time.sleep(5)

    with tab5:
        st.header("🧠 Model Başarımı")

        st.markdown(
            "Bu sekmede, makine öğrenmesi modelimizin doğruluk (accuracy), hassasiyet (precision), geri çağırma (recall) ve F1 skorunu görebilirsiniz.")

        try:
            with open("model/performance_report.txt", "r") as f:
                report_txt = f.read()

            st.code(report_txt, language="text")
            st.success("✅ Son model başarı raporu başarıyla yüklendi.")

        except FileNotFoundError:
            st.warning(
                "⚠️ Performans raporu bulunamadı. Lütfen önce `ml_train.py` dosyasını çalıştırarak modeli eğitin.")


if __name__ == "__main__":
    main()
