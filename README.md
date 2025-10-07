# 🧠 Sales.AI – FastAPI Satış Tahmin Servisi

**Sales.AI**, geçmiş satış verilerini kullanarak **ürün** ve **kategori** bazında **günlük satış tahminleri** üreten bir makine öğrenmesi servisidir.  
Uygulama **FastAPI** ile geliştirilmiş olup hem kullanıcı bazlı hem de genel kategori bazlı tahminleri destekler.

---

## 🚀 Özellikler

- 📈 **Tarih bazlı öğrenme:** Satış, kategori, kampanya ve kullanıcı verilerine göre model eğitimi  
- 🧩 **İki model desteği:**
  - Ürün bazlı satış tahmin modeli  
  - Kategori bazlı genel veya kullanıcı bazlı satış tahmin modeli  
- 🔁 **CSV dosyasından eğitim:** Basit bir `POST /train` isteğiyle yeni verilerle model eğitimi  
- ⚡ **Hızlı API:** FastAPI üzerinde JSON tabanlı tahmin servisleri  
- 💾 **Model saklama:** Eğitim sonrası modeller `models_bin/` klasöründe saklanır  

---

## ⚙️ Kurulum

```bash
# Sanal ortam oluştur
python -m venv venv
source venv/bin/activate     # (Windows: venv\Scripts\activate)

# Gerekli kütüphaneleri yükle
pip install -r requirements.txt

# Uygulamayı başlat
uvicorn app:app --reload
```

## 📚 API Endpoint'leri
#### 1. Model Eğitimi

```http
  POST /train
```

| Parametre | Tip     | Açıklama                |
| :-------- | :------- | :------------------------- |
| `csv_file` | `form-data (.csv)` | Eğitim verilerini içeren CSV dosyası. |

📤 Response
```json
{
  "message": "Satış ve kategori modelleri başarıyla eğitildi."
}
```

[✅ Örnek CSV Formatı](https://github.com/Talipbl/sales-ai/blob/main/data/sales.csv "sales.csv")


🔹 2. Ürün Bazlı Satış Tahmini

Belirli bir kullanıcı ve ürün için tarih aralığında günlük satış tahminleri üretir.
```http
  POST /predict
```
📥 Request (JSON)
```json
{
  "user_id": 101,
  "product_code": "ABC123",
  "start_date": "2025-06-01",
  "end_date": "2025-06-07",
  "campaign": 0
}
```

📤 Response
```json
{
  "success": true,
  "predictions": [
    {"date": "2025-06-01", "predicted_sales": 48},
    {"date": "2025-06-02", "predicted_sales": 51},
    {"date": "2025-06-03", "predicted_sales": 47}
  ]
}
```

🔹 3. Kategori Bazlı Satış Tahmini

Belirli bir kategori için kullanıcı bazlı veya genel satış tahmini üretir.
```http
  POST /predict/category
```

📥 Request (JSON)
```json
  {
    "start_date": "2025-06-01",
    "end_date": "2025-06-07",
    "user_id": 101,
    "campaign": 1
  }
```

Eğer user_id gönderilmezse, genel kategori tahmini yapılır.

📤 Response
```json
  {
    "category": "Drinks",
    "predictions": [
      {"date": "2025-06-01", "predicted_sales": 210},
      {"date": "2025-06-02", "predicted_sales": 190}
    ]
  }
```


## Model Bilgisi

Eğitim sürecinde src/trainer.py dosyasındaki train_model_sales() ve train_model_category() fonksiyonları çağrılır.
Tahmin süreçleri src/predictor.py dosyasında tanımlıdır:
predict_sales() → Ürün bazlı tahmin
predict_user_category_sales() → Kullanıcı bazlı kategori tahmini
predict_general_category_sales() → Genel kategori tahmini

📊 Örnek Kullanım (curl)
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
-H "Content-Type: application/json" \
-d '{
  "user_id": 101,
  "product_code": "ABC123",
  "start_date": "2025-06-01",
  "end_date": "2025-06-07",
  "campaign": 0
}'
```

## 💬 Notlar

Tarih formatı YYYY-MM-DD olmalıdır.
start_date, end_date’den büyük olamaz.
Kampanya alanı (0 veya 1) modele doğrudan girdi olarak kullanılır.
CSV dosyası yüklendiğinde önceki eğitim verisi üzerine yazılır.

## Geliştirici Notu
Proje, çoklu kullanıcı ve çoklu ürün destekleyen bir satış tahmin altyapısının temelini oluşturur.
FastAPI yapısı sayesinde mikro servis olarak kolayca konteynerleştirilebilir veya bir e-ticaret platformuna entegre edilebilir.
