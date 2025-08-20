# Gerçek Zamanlı Anomali Tespiti (SQLite + Streamlit + FastAPI)

Bu proje, kullanıcı işlemlerini gerçek zamanlı olarak izleyen, olağandışı (anormal) davranışları tespit eden ve bu verileri kullanıcı dostu bir arayüz üzerinden görselleştiren bir sistemdir. Makine öğrenmesi tabanlı model sayesinde işlemler analiz edilir, şüpheli hareketler işaretlenir ve istenirse Telegram üzerinden anında bildirim gönderilir. Sistem hem manuel giriş hem de sahte API verileri ile test edilebilir, ayrıca kullanıcı bazlı risk skorlarını otomatik olarak hesaplar.

---

## ✨ Özellikler

* **SQLite** veritabanı ile kolay kurulum
* **RandomForest** tabanlı anomali modeli + encoder dosyaları (`.pkl`)
* **Gerçek zamanlı veri girişi**:

  * Streamlit UI üzerinden manuel giriş
  * CLI aracı ile terminalden işlem ekleme
  * Sahte işlem üreten **FastAPI** servisi
* **Kullanıcı bazlı görselleştirmeler** ve metrikler
* **Risk skoru** (0–100) her kullanıcı için otomatik güncellenir
* **Her 100 işlemde bir** model otomatik yeniden eğitilir
* **Opsiyonel** Telegram bildirimi ile anomali uyarısı

---

## 🧭 İçindekiler

* [Proje Yapısı](#proje-yapısı)
* [Gereksinimler](#gereksinimler)
* [Hızlı Başlangıç](#hızlı-başlangıç)
* [Modeli Eğitme](#modeli-eğitme)
* [Uygulamaları Çalıştırma](#uygulamaları-çalıştırma)
* [Sistem Nasıl Çalışır](#sistem-nasıl-çalışır)
* [Arayüz Kılavuzu](#arayüz-kılavuzu)
* [Konfigürasyon](#konfigürasyon)

---

## Proje Yapısı

```
├─ anomaly_detection.db   # SQLite veritabanı
├─ app.py                 # Streamlit arayüzü
├─ insert_and_detect.py   # İşlem ekleme, anomali tespiti, Telegram bildirimi
├─ interactive_insert.py  # CLI aracı ile işlem ekleme
├─ main.py                # Veritabanı tablolarını oluşturur
├─ ml_prepare.py          # Veri hazırlama, encoder önizleme
├─ ml_train.py            # Model eğitimi, encoder kayıtları, grafikler
├─ mock_api.py            # FastAPI ile sahte veri üretici servis
├─ populate_db.py         # Kullanıcı ve sahte işlem verisi ekler
├─ telegram_chat_id.py    # Telegram chat ID alma
├─ update_schema.py       # Tabloya yeni sütun ekleme (fix gerekebilir)
├─ visualize_data.py      # Matplotlib ile grafik çizme
└─ model/                 # Model ve encoder dosyaları
```

---

## Gereksinimler

* **Python 3.10+**
* `pip install -r requirements.txt`

---

## Hızlı Başlangıç

### A) Var olan veritabanı ile

```bash
python update_schema.py
python ml_train.py
streamlit run app.py
```

### B) Sıfırdan başlatmak için

```bash
python main.py
python update_schema.py
python populate_db.py
python ml_train.py
```

---

## Modeli Eğitme

```bash
python ml_train.py
```

* `model/` klasöründe model ve encoder dosyaları oluşur.
* ROC, PR curve ve feature importance grafikleri kaydedilir.

---

## Uygulamaları Çalıştırma

* **Mock API**:

```bash
uvicorn mock_api:app --reload --port 8000
```

* **Streamlit UI**:

```bash
streamlit run app.py
```

* **CLI**:

```bash
python interactive_insert.py
```

---

## Sistem Nasıl Çalışır

* İşlemler modele encode edilerek verilir.
* RandomForest ile anomali olasılığı hesaplanır.
* Eğer işlem gece (saat < 6) ve tutar > 1500 TL ise doğrudan anomali kabul edilir.
* Kullanıcı risk skoru güncellenir.
* 100 işlemde bir model yeniden eğitilir.
* Anomali durumunda Telegram bildirimi gönderilebilir.

---

## Arayüz Kılavuzu

1. **➕ Transaction Ekle**: Manuel işlem girişi
2. **📈 Grafiksel Analiz**: Kullanıcıya ait özet ve grafikler
3. **🚨 Anomaliler**: Anormal işlemler listesi ve CSV export
4. **📡 Canlı Veri Akışı**: Mock API üzerinden otomatik veya belirli sayıda işlem çekme
5. **🧠 Model Performansı**: ROC, PR grafikleri ve feature importance

---

## Konfigürasyon

* Telegram bildirimleri için `TELEGRAM_BOT_TOKEN` ve `TELEGRAM_CHAT_ID` ortam değişkenleri ayarlanmalıdır.

---

# Real-Time Anomaly Detection (SQLite + Streamlit + FastAPI)

This project monitors user transactions in real-time, detects unusual (anomalous) behaviors using a machine learning model, and visualizes the results through a user-friendly Streamlit interface. With the help of a RandomForest-based model, transactions are analyzed, suspicious activities are flagged, and instant alerts can be sent via Telegram if desired. The system supports manual entry, simulated API data, and automatically computes risk scores for each user.

---

## ✨ Features

* **SQLite** backend with simple setup
* **RandomForest** anomaly model + label encoders (`.pkl`)
* **Real-time ingest**:

  * Manual entry via Streamlit UI
  * CLI tool for terminal input
  * Mock **FastAPI** service for simulated transactions
* **User-based metrics and visualization**
* **Risk score** (0–100) automatically updated per user
* **Retrains every 100 transactions**
* **Optional** Telegram anomaly alerts

---

## 🧭 Table of Contents

* [Project Structure](#project-structure)
* [Prerequisites](#prerequisites)
* [Quick Start](#quick-start)
* [Train the Model](#train-the-model)
* [Run the Apps](#run-the-apps)
* [How It Works](#how-it-works)
* [UI Guide](#ui-guide)
* [Configuration](#configuration)

---

## Project Structure

```
├─ anomaly_detection.db   # SQLite database
├─ app.py                 # Streamlit UI
├─ insert_and_detect.py   # Insert, anomaly detection, Telegram alerts
├─ interactive_insert.py  # CLI manual insert
├─ main.py                # Create database tables
├─ ml_prepare.py          # Data preparation & encoder preview
├─ ml_train.py            # Train model, save encoders & charts
├─ mock_api.py            # FastAPI mock transaction service
├─ populate_db.py         # Seed users & transactions
├─ telegram_chat_id.py    # Get Telegram chat ID
├─ update_schema.py       # Add columns (fix may be required)
├─ visualize_data.py      # Quick matplotlib plots
└─ model/                 # Model & encoder files
```

---

## Prerequisites

* **Python 3.10+**
* `pip install -r requirements.txt`

---

## Quick Start

### A) Using existing DB

```bash
python update_schema.py
python ml_train.py
streamlit run app.py
```

### B) Fresh start

```bash
python main.py
python update_schema.py
python populate_db.py
python ml_train.py
```

---

## Train the Model

```bash
python ml_train.py
```

* Creates model and encoder files in `model/`
* Saves ROC, PR curve, and feature importance charts

---

## Run the Apps

* **Mock API**:

```bash
uvicorn mock_api:app --reload --port 8000
```

* **Streamlit UI**:

```bash
streamlit run app.py
```

* **CLI**:

```bash
python interactive_insert.py
```

---

## How It Works

* Encodes transaction fields
* Predicts anomaly probability with RandomForest
* Hard rule: if `hour < 6` and `amount > 1500` → anomaly
* Updates user risk score
* Retrains after 100 inserts
* Sends Telegram alert if anomaly

---

## UI Guide

1. **➕ Add Transaction**: Manual input
2. **📈 Graphical Analysis**: User metrics & graphs
3. **🚨 Anomalies**: List/export anomaly transactions
4. **📡 Live Data Stream**: Auto or fixed-count fetch from API
5. **🧠 Model Performance**: ROC, PR curves, feature importance

---

## Configuration

* For Telegram alerts, set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` as environment variables.
