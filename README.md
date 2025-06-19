# 🚨 Anomali Tespiti Sistemi

Bu proje, kullanıcıların geçmiş işlem alışkanlıklarına göre gerçek zamanlı olarak şüpheli (anomali) işlemleri tespit etmeyi amaçlayan bir sistemdir. 

## 📌 Proje Özeti
- Kullanıcının geçmiş 10 işlemine bakarak alışkanlık profili oluşturur.
- Yeni gelen işlemleri bu profile göre analiz eder.
- Anomalileri işaretler, raporlar ve görselleştirir.
- Streamlit ile görsel arayüz sağlar.

## 📁 Proje Dosyaları

| Dosya Adı | Açıklama |
|-----------|----------|
| `main.py` | Veritabanı tablolarını (`users`, `transactions`) oluşturur. |
| `populate_db.py` | Sahte kullanıcı ve işlem verisi üretir. |
| `insert_and_detect.py` | Anomali tespiti, kullanıcı profili çıkarımı ve işlem ekleme fonksiyonlarını içerir. |
| `interactive_insert.py` | Terminal tabanlı işlem ekleme arayüzüdür. |
| `visualize_data.py` | Matplotlib ile terminalde grafiksel analiz sağlar. |
| `app.py` | Streamlit tabanlı web arayüzüdür. Gerçek zamanlı işlem ekleme ve grafikler içerir. |

---

## 🧪 Kurulum ve Kullanım

### 1. Gerekli Kütüphaneler

```bash
pip install streamlit pandas matplotlib
```

### 2. Veritabanını Oluşturma

```bash
python main.py
```

### 3. Sahte Veri Oluşturma (Opsiyonel)

```bash
python populate_db.py
```

### 4. Streamlit Arayüzünü Başlatma

```bash
streamlit run app.py
```

---

## 🧠 Kullanılan Teknolojiler

- **Python 3.x**
- **SQLite** — Yerel veritabanı
- **Pandas** — Veri işleme
- **Matplotlib** — Grafik çizimi (CLI)
- **Streamlit** — Web arayüzü

---

## 📊 Özellikler

- [x] Kullanıcı alışkanlık profili çıkarma
- [x] Zaman, tutar ve lokasyon bazlı anomaly kontrolü
- [x] Anomali oranı, saat dağılımı, geçmiş tablosu ve CSV çıktısı
- [x] Kullanıcı seçimiyle bireysel analiz
- [x] Modern ve açıklayıcı arayüz

---

## 📌 Örnek Ekran Görüntüsü
![image](https://github.com/user-attachments/assets/72c3a87d-0407-4897-b920-cf4de194df05),
![image](https://github.com/user-attachments/assets/e431ca2c-0f04-4695-b724-d0f11409f2ee),
![image](https://github.com/user-attachments/assets/3d5e51e3-f95c-4996-8bb0-cdb0733fa77a)

---

## 👤 Katkıda Bulunanlar
- Onur Çokyiğit

---

## 📝 Lisans
Bu proje MIT lisansı ile lisanslanmıştır.

---

Herhangi bir geri bildiriminiz veya katkı isteğiniz varsa lütfen [issues](https://github.com/OnurCokyigit/anomaly-detector/issues) sekmesini kullanmaktan çekinmeyin 🙌
