import pandas as pd
import pickle
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import numpy as np

def evaluate_model(csv_path, model_path):
    # Veri oku
    df = pd.read_csv(csv_path)
    df["Tarih"] = pd.to_datetime(df["Tarih"])

    # Feature engineering örneği
    df["Gun"] = df["Tarih"].dt.dayofweek
    df["Ay"] = df["Tarih"].dt.month
    df["Hafta"] = df["Tarih"].dt.isocalendar().week
    df["HaftaSonu"] = df["Tarih"].dt.weekday >= 5
    df["HaftaSonu"] = df["HaftaSonu"].astype(int)

    # Hedef ve özellikler
    target = "Sales" if "Sales" in df.columns else "SatisAdedi"
    features = ["Gun", "Ay", "Hafta", "HaftaSonu", "UserID", "UrunKategori"]

    # Kategorik değişkenleri one-hot encode et
    df = pd.get_dummies(df, columns=["UrunKategori", "UserID"], drop_first=True)

    X = df[features + [col for col in df.columns if col.startswith("UrunKategori_") or col.startswith("UserID_")]]
    y = df[target]

    # Eğitim/test bölmesi
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Model yükle
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    # Tahmin
    y_pred = model.predict(X_test)

    # Performans metrikleri
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"📊 Evaluation Results:")
    print(f"  ✅ RMSE: {rmse:.2f}")
    print(f"  ✅ MAE : {mae:.2f}")
    print(f"  ✅ R²  : {r2:.4f}")

    return {"rmse": rmse, "mae": mae, "r2": r2}
