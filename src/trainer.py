import pandas as pd
import lightgbm as lgb
import pickle
import os

def feature_engineering_sales(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df["Day"] = df["Date"].dt.dayofweek
    df["Month"] = df["Date"].dt.month
    df["Week"] = df["Date"].dt.isocalendar().week
    df["WeekEnd"] = df["Day"].apply(lambda x: 1 if x >= 5 else 0)

    df = df.sort_values(by=["UserID", "ProductCode", "Date"])
    df["Lag_1"] = df.groupby(["UserID", "ProductCode"])["SalesQuantity"].shift(1)
    df["RollingMean_3"] = (
        df.groupby(["UserID", "ProductCode"])["SalesQuantity"]
        .shift(1).rolling(window=3).mean()
    )
    df["UserCatAvg"] = df.groupby(["UserID", "Category"])["SalesQuantity"].transform("mean")
    
    # Campaign mutlaka 0 veya 1 olarak olmalı
    df["Campaign"] = df["Campaign"].fillna(0).astype(int)

    df["Lag_1"] = df["Lag_1"].fillna(0)
    df["RollingMean_3"] = df["RollingMean_3"].fillna(0)
    df = df.dropna()

    return df

def feature_engineering_category(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df["Day"] = df["Date"].dt.dayofweek
    df["Month"] = df["Date"].dt.month
    df["Week"] = df["Date"].dt.isocalendar().week
    df["WeekEnd"] = df["Day"].apply(lambda x: 1 if x >= 5 else 0)

    # Kategori bazında gruplama ve feature yaratma
    df = df.sort_values(by=["Category", "Date"])
    # Önceki gün satış adedi lagı (kategori bazında)
    df["Lag_1"] = df.groupby("Category")["SalesQuantity"].shift(1)
    # Son 3 günün ortalaması kategori bazında
    df["RollingMean_3"] = (
        df.groupby("Category")["SalesQuantity"]
        .shift(1).rolling(window=3).mean()
    )

    df["Lag_1"] = df["Lag_1"].fillna(0)
    df["RollingMean_3"] = df["RollingMean_3"].fillna(0)

    user_cat_avg = df.groupby(["UserID", "Category"])["SalesQuantity"].transform("mean")
    df["UserCatAvg"] = user_cat_avg.fillna(0)

    # Campaign mutlaka 0 veya 1 olarak olmalı
    df["Campaign"] = df["Campaign"].fillna(0).astype(int)
    df = df.dropna()

    return df

def train_model_sales(csv_path, sales_model_path):
    df = pd.read_csv(csv_path)
    df = feature_engineering_sales(df)

    features = ["Day", "Month", "Week", "WeekEnd", "Lag_1", "RollingMean_3", "UserCatAvg", "Campaign"]
    target = "SalesQuantity"

    X = df[features]
    y = df[target]

    if os.path.exists(sales_model_path):
        with open(sales_model_path, "rb") as f:
            model = pickle.load(f)
        model = model.fit(X, y, init_model=model.booster_)  # devamlı öğrenme için fit yerine refit
    else:
        model = lgb.LGBMRegressor()
        model.fit(X, y)

    with open(sales_model_path, "wb") as f:
        pickle.dump(model, f)

def train_model_category(csv_path, category_model_path):
    df = pd.read_csv(csv_path)
    df = feature_engineering_category(df)

    features = ["Day", "Month", "Week", "WeekEnd", "Lag_1", "RollingMean_3", "Category", "UserCatAvg", "Campaign"]
    target = "SalesQuantity"

    X = df[features]
    y = df[target]

    if os.path.exists(category_model_path):
        with open(category_model_path, "rb") as f:
            model = pickle.load(f)
        model = model.fit(X, y, init_model=model.booster_)
    else:
        model = lgb.LGBMRegressor()
        model.fit(X, y)

    with open(category_model_path, "wb") as f:
        pickle.dump(model, f)