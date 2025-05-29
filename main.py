from fastapi import FastAPI, UploadFile, File, HTTPException
from src.trainer import train_model_sales, train_model_category
from src.predictor import predict_sales, predict_user_category_sales, predict_general_category_sales
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import shutil
import os

app = FastAPI()

DATA_PATH = "data/sales.csv"
SALES_MODEL_PATH = "models_bin/sales_model.pkl"
CATEGORY_MODEL_PATH = "models_bin/categories_model.pkl"

# Eğitim endpoint'i
@app.post("/train", summary="Tahmin modelini eğitir. .csv dosyası kabul eder.")
async def train(csv_file: UploadFile = File(...)):
    if csv_file.filename.endswith(".csv") is False:
        raise HTTPException(status_code=400, detail="CSV dosyası yüklemelisin.")
    
    os.makedirs("data", exist_ok=True)
    with open(DATA_PATH, "wb") as buffer:
        shutil.copyfileobj(csv_file.file, buffer)

    train_model_sales(DATA_PATH, SALES_MODEL_PATH)
    train_model_category(DATA_PATH, CATEGORY_MODEL_PATH)
    return {"message": "Satış ve kategori modelleri başarıyla eğitildi."}

# Tahmin isteği için model
class PredictionRequest(BaseModel):
    user_id: int = Field(..., example=101)
    product_code: str = Field(..., example="ABC123")
    start_date: str = Field(..., example="2025-06-01")
    end_date: str = Field(..., example="2025-06-07")
    campaign: int = Field(0, ge=0, le=1, example=0)

@app.post("/predict", summary="Belirli bir kullanıcı ve ürün için satış tahmini yapar.")
def predict_sales_enp(req: PredictionRequest):
    try:
        # Tarih formatı kontrolü
        start = datetime.strptime(req.start_date, "%Y-%m-%d")
        end = datetime.strptime(req.end_date, "%Y-%m-%d")
        if start > end:
            raise HTTPException(status_code=400, detail="start_date, end_date'ten sonra olamaz.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Tarih formatı YYYY-MM-DD olmalı.")

    try:
        result = predict_sales(
            user_id=req.user_id,
            product_code=req.product_code,
            start_date=req.start_date,
            end_date=req.end_date,
            campaign=req.campaign,
            model_path=SALES_MODEL_PATH,
            data_path=DATA_PATH
        )
        return {"success": True, "predictions": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model tahmin hatası: {str(e)}")

class CategoryPredictionRequest(BaseModel):
    start_date: str = Field(..., example="2025-06-01")
    end_date: str = Field(..., example="2025-06-07")
    user_id: Optional[int] = None
    campaign: Optional[int] = 0  # Default kampanya yok


@app.post("/predict/category", summary="Kategori için satış tahmini yapar. Kullanıcı bazlı yada genel tahmin yapar.")
def predict_category(req: CategoryPredictionRequest):
    if req.user_id:
        result = predict_user_category_sales(
            user_id=req.user_id,
            start_date=req.start_date,
            end_date=req.end_date,
            campaign=req.campaign,
            model_path=CATEGORY_MODEL_PATH,
            data_path=DATA_PATH
        )
    else:
        result = predict_general_category_sales(
            start_date=req.start_date,
            end_date=req.end_date,
            campaign=req.campaign,
            model_path=CATEGORY_MODEL_PATH,
            data_path=DATA_PATH
        )
    return result
