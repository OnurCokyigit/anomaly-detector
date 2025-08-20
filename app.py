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
    st.set_page_config(page_title="Anomaly Detection", layout="wide")
    st.title("📊 Anomaly Detection System")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ Add Transaction",
        "📈 Graphical Analysis",
        "🚨 Anomalies",
        "📡 Live Data Stream",
        "🧠 Model Performance"
    ])

    with tab1:
        st.header("Add New Transaction")
        user_ids = get_user_ids()
        user_id = st.selectbox("Select User", user_ids)
        amount = st.number_input("Transaction Amount (TL)", min_value=1.0, step=1.0)
        location = st.selectbox("Select Location", get_location_list())

        date = st.date_input("Transaction Date", datetime.now().date())
        txn_time_input = st.time_input("Transaction Time", datetime.now().time())
        txn_time = datetime.combine(date, txn_time_input)
        txn_time_str = txn_time.strftime("%Y-%m-%d %H:%M:%S")

        transaction_type = st.text_input("Transaction Type (e.g., payment, transfer)")
        device_type = st.text_input("Device Type (e.g., Mobile, Desktop)")
        channel = st.text_input("Channel (e.g., Web, App)")
        browser_info = st.text_input("Browser Info (e.g., Chrome)")
        os_type = st.text_input("Operating System (e.g., Windows, Android)")
        ip_address = st.text_input("IP Address")
        session_duration = st.number_input("Session Duration (seconds)", min_value=0.0, step=1.0)

        if st.button("💾 Save Transaction"):
            result = insert_transaction(
                user_id, amount, txn_time_str, location,
                transaction_type, device_type, channel,
                browser_info, os_type, ip_address, session_duration
            )

            if result is None:
                st.markdown("""
                    <div style='background-color:#fff3cd; padding:10px; border-radius:10px;'>
                        ⚠️ This transaction is already recorded.
                    </div>
                """, unsafe_allow_html=True)
            elif result == 1:
                st.markdown("""
                    <div style='background-color:#f8d7da; padding:10px; border-radius:10px;'>
                        ❗ Anomaly detected and the transaction was recorded.
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style='background-color:#d4edda; padding:10px; border-radius:10px;'>
                        ✅ Transaction is normal and has been successfully recorded.
                    </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.header("User-Based Visualization")
        user_ids = get_user_ids()
        selected_user = st.selectbox("Select user for chart", user_ids, key="viz_user")
        df = load_user_data(selected_user)

        if df.empty:
            st.markdown("""
                <div style='background-color:#fff3cd; padding:10px; border-radius:10px;'>
                    There is no transaction data for this user.
                </div>
            """, unsafe_allow_html=True)
        else:
            st.subheader("📊 Summary Metrics")
            total_txns = len(df)
            anomaly_count = df['is_anomaly'].sum()
            anomaly_rate = (anomaly_count / total_txns) * 100
            avg_amount = df['amount'].mean()

            # ✅ RISK METRIC ADDED
            conn = sqlite3.connect("anomaly_detection.db")
            cursor = conn.cursor()
            cursor.execute("SELECT risk_score FROM users WHERE user_id = ?", (selected_user,))
            risk = cursor.fetchone()[0]
            conn.close()

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("📦 Total Transactions", total_txns)
            col2.metric("⚠️ Anomaly Count", anomaly_count)
            col3.metric("📉 Anomaly Rate", f"{anomaly_rate:.1f}%")
            col4.metric("💸 Average Amount", f"{avg_amount:.2f} TL")
            col5.metric("🔥 Risk Score", f"{risk} / 100")

            st.subheader("📌 Anomaly Distribution")
            counts = df["is_anomaly"].value_counts().rename({0: "Normal", 1: "Anomaly"})
            st.bar_chart(counts)

            st.subheader("🕒 Hourly Distribution")
            df["txn_time"] = pd.to_datetime(df["txn_time"])
            df["hour"] = df["txn_time"].dt.hour
            st.bar_chart(df["hour"].value_counts().sort_index())

    with tab3:
        st.header("🚨 Anomaly Transactions")
        user_ids = get_user_ids()
        selected_user = st.selectbox("Select user to view anomalies", user_ids, key="anomaly_user")
        df = load_user_data(selected_user)

        if df.empty or df['is_anomaly'].sum() == 0:
            st.markdown("""
                <div style='background-color:#d1ecf1; padding:10px; border-radius:10px;'>
                    There are no anomaly transactions for this user.
                </div>
            """, unsafe_allow_html=True)
        else:
            df_anomalies = df[df["is_anomaly"] == 1].copy()
            df_anomalies["txn_time"] = pd.to_datetime(df_anomalies["txn_time"])
            df_anomalies = df_anomalies.sort_values("txn_time", ascending=False)
            df_anomalies["anomaly_score"] = df_anomalies["anomaly_score"].fillna(0).astype(float)

            st.subheader(f"🔎 {len(df_anomalies)} Anomaly Transactions for User {selected_user}")

            cols_to_show = [
                "txn_time", "amount", "location", "transaction_type", "device_type",
                "channel", "browser_info", "os_type", "ip_address", "session_duration",
                "anomaly_score"
            ]

            st.dataframe(df_anomalies[cols_to_show])

            st.download_button(
                label="📥 Download Anomalies (CSV)",
                data=df_anomalies[cols_to_show].to_csv(index=False).encode("utf-8"),
                file_name=f"user_{selected_user}_anomalies.csv",
                mime="text/csv"
            )

            st.markdown("---")
            st.bar_chart(df_anomalies.set_index("txn_time")["amount"])
            st.caption("🟠 Distribution of anomaly amounts over the time series")

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
        st.header("📡 Live Data Stream (API Based)")
        st.markdown("In this tab, you can fetch data via API.")

        mode = st.radio("Select data fetch mode:", ["🔁 Automatic Stream", "🔢 Fetch by Number"], horizontal=True)

        if "stop_stream" not in st.session_state:
            st.session_state["stop_stream"] = False

        status_box = st.empty()
        result_box = st.empty()

        def handle_result(data, index=None, total=None):
            txn_info = f"📥 New Data Received"
            if index is not None and total is not None:
                txn_info += f" ({index}/{total})"

            status_box.markdown(f"""
                <div style="background-color:#f0f2f6; padding:10px; border-radius:10px">
                    <b>{txn_info}:</b><br>
                    👤 <b>User ID:</b> {data['user_id']}<br>
                    💸 <b>Amount:</b> {data['amount']} TL<br>
                    🗺️ <b>Location:</b> {data['location']}<br>
                    ⏰ <b>Time:</b> {data['txn_time']}<br>
                    🧾 <b>Transaction Type:</b> {data['transaction_type']}<br>
                    💻 <b>Device:</b> {data['device_type']} / {data['channel']}<br>
                    🌐 <b>Browser:</b> {data['browser_info']}<br>
                    🧠 <b>Operating System:</b> {data['os_type']}<br>
                    📶 <b>IP:</b> {data['ip_address']}<br>
                    ⏱️ <b>Session Duration:</b> {data['session_duration']} s
                </div>
            """, unsafe_allow_html=True)

            is_anomaly, anomaly_score = insert_transaction(
                user_id=data["user_id"],
                amount=data["amount"],
                txn_time=data["txn_time"],
                location=data["location"],
                transaction_type=data.get("transaction_type"),
                device_type=data.get("device_type"),
                channel=data.get("channel"),
                browser_info=data.get("browser_info"),
                os_type=data.get("os_type"),
                ip_address=data.get("ip_address"),
                session_duration=data.get("session_duration")
            )

            if is_anomaly == 1:
                result_box.markdown(f"""
                    <div style='background-color:#f8d7da; padding:10px; border-radius:10px;'>
                        🚨 <b>Anomaly Detected!</b><br>
                        🔎 <b>Model Score:</b> {anomaly_score:.2f}
                    </div>
                """, unsafe_allow_html=True)

                bar_color = (
                    "#28a745" if anomaly_score < 0.4 else  # green
                    "#ffc107" if anomaly_score < 0.75 else  # yellow
                    "#dc3545"  # red
                )

                result_box.markdown(f"""
                    <div style="margin-top: 10px;">
                        <b>Anomaly Score Bar:</b>
                        <div style="background-color:#e9ecef; width: 100%; height: 20px; border-radius: 10px;">
                            <div style="width: {anomaly_score * 100:.1f}%; background-color:{bar_color};
                                        height: 100%; border-radius: 10px;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                result_box.markdown(f"""
                    <div style='background-color:#d4edda; padding:10px; border-radius:10px;'>
                        ✅ <b>Normal Transaction</b><br>
                        🔎 <b>Model Score:</b> {anomaly_score:.2f}
                    </div>
                """, unsafe_allow_html=True)

        if mode == "🔁 Automatic Stream":
            start_button = st.button("▶️ Start Automatic Stream")
            stop_button = st.button("⛔ Stop")

            if stop_button:
                st.session_state["stop_stream"] = True

            if start_button:
                st.session_state["stop_stream"] = False
                status_box.info("📡 Automatic data stream started...")
                while not st.session_state["stop_stream"]:
                    try:
                        response = requests.get("http://127.0.0.1:8000/transaction")
                        if response.status_code == 200:
                            data = response.json()
                            handle_result(data)
                        else:
                            status_box.warning(f"⚠️ Unexpected response: {response.status_code}")
                    except Exception as e:
                        result_box.error(f"⚠️ Error: {e}")
                    time.sleep(2)

        if mode == "🔢 Fetch by Number":
            num_requests = st.number_input("📦 How many transactions to fetch?", min_value=1, max_value=100, value=5)
            start_fixed = st.button("▶️ Fetch Specified Number", key="start_fixed")
            stop_fixed = st.button("⛔ Stop", key="stop_fixed")

            if stop_fixed:
                st.session_state["stop_stream"] = True

            if start_fixed:
                st.session_state["stop_stream"] = False
                status_box.info("🔢 Fetching specified number of data...")

                for i in range(int(num_requests)):
                    if st.session_state["stop_stream"]:
                        status_box.warning("⛔ Data fetch stopped.")
                        break

                    try:
                        response = requests.get("http://127.0.0.1:8000/transaction")
                        if response.status_code == 200:
                            data = response.json()
                            handle_result(data, i + 1, num_requests)
                        else:
                            status_box.warning(f"⚠️ Unexpected response: {response.status_code}")
                    except Exception as e:
                        result_box.error(f"⚠️ Error: {e}")

                    time.sleep(5)

    with tab5:
        st.header("🧠 Model Performance")
        st.markdown(
            "In this tab, you can view the machine learning model's accuracy, precision, recall, and F1 score."
        )
        try:
            with open("model/performance_report.txt", "r") as f:
                report_txt = f.read()

            st.code(report_txt, language="text")
            st.success("✅ Latest model performance report loaded successfully.")
        except FileNotFoundError:
            st.warning(
                "⚠️ Performance report not found. Please train the model first by running `ml_train.py`."
            )

        st.subheader("📉 ROC Curve")

        try:
            st.image("model/roc_curve.png", caption="ROC Curve")
        except Exception as e:
            st.warning(f"Could not load ROC curve image: {e}")

        st.subheader("📈 Precision-Recall Curve")

        try:
            st.image("model/pr_curve.png", caption="Precision-Recall Curve")
        except Exception as e:
            st.warning(f"Could not load Precision-Recall curve image: {e}")

        st.subheader("🔍 Feature Importance Chart")

        try:
            df_feat = pd.read_csv("model/feature_importance.csv")
            if "feature" in df_feat.columns and "importance" in df_feat.columns:
                st.bar_chart(df_feat.set_index("feature"))
            else:
                st.warning("Expected columns not found in the CSV.")
        except Exception as e:
            st.warning(f"Could not load feature importance chart: {e}")

        st.caption(
            "📌 This chart shows which features the model considers most important for decision making. "
            "A higher score means the model pays more attention to that feature."
        )


if __name__ == "__main__":
    main()
