import pandas as pd
import pickle
from datetime import datetime, timedelta

def predict_sales(user_id, product_code, start_date, end_date, model_path, data_path, campaign = 0):

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    df = pd.read_csv(data_path)
    df["Date"] = pd.to_datetime(df["Date"])

    # İlgili kullanıcı ve ürün geçmişi
    product_history = df[(df["UserID"] == user_id) & (df["ProductCode"] == product_code)].copy()
    product_history = product_history.sort_values("Date")

    # Ürün kategorisi tespiti
    if not product_history.empty and "ProductCode" in product_history.columns:
        product_category = product_history["ProductCode"].iloc[-1]
    else:
        product_category = "Unknown"  # default kategori
    product_category_code = pd.Series([product_category]).astype('category').cat.codes[0]

    # Kullanıcının bu kategoriye ait ortalama satışı
    if not product_history.empty:
        user_cat_avg = df[
            (df["UserID"] == user_id) & (df["ProductCode"] == product_category)
        ]["SalesQuantity"].mean()
    else:
        user_cat_avg = 0

    date_ranges = pd.date_range(start=start_date, end=end_date)
    predictions = []

    for date in date_ranges:
        # Geçmiş lag ve rolling hesaplama
        recent_sales = product_history[product_history["Date"] < date]["SalesQuantity"]
        lag_1 = recent_sales.iloc[-1] if len(recent_sales) > 0 else 0
        rolling = recent_sales.tail(3).mean() if len(recent_sales) >= 3 else lag_1

        input_row = {
            "Day": date.dayofweek,
            "Month": date.month,
            "Week": date.isocalendar()[1],
            "WeekEnd": 1 if date.weekday() >= 5 else 0,
            "Lag_1": lag_1,
            "RollingMean_3": rolling,
            "UserCatAvg": user_cat_avg,
            "Campaign": campaign
        }

        prediction = model.predict(pd.DataFrame([input_row]))[0]
        predictions.append({
            "Date": date.strftime("%Y-%m-%d"),
            "EstimatedSales": round(prediction)
        })

        # Günlük tahmini simüle edip sonraki gün için geçmişe ekleyelim (recursive tahmin gibi)
        product_history = pd.concat([
            product_history,
            pd.DataFrame([{
                "Date": date,
                "UserID": user_id,
                "ProductCode": product_code,
                "SalesQuantity": prediction,
                "ProductCategory": product_category
            }])
        ], ignore_index=True)

    return predictions


def predict_user_category_sales(user_id, start_date, end_date, model_path, data_path, campaign = 0):
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    df = pd.read_csv(data_path)
    df["Date"] = pd.to_datetime(df["Date"])

    df_user = df[df["UserID"] == user_id]
    if df_user.empty:
        return []

    date_ranges = pd.date_range(start=start_date, end=end_date)
    categories = df_user["Category"].unique()

    results = []
    for category in categories:
        kat_df = df_user[df_user["Category"] == category].sort_values("Date")
        lag_1 = kat_df["SalesQuantity"].iloc[-1] if not kat_df.empty else 0
        rolling = kat_df["SalesQuantity"].tail(3).mean() if len(kat_df) >= 3 else lag_1
        user_cat_avg = kat_df["SalesQuantity"].mean() if not kat_df.empty else 0

        total_pred = 0
        for date in date_ranges:
            input_row = {
                "Day": date.dayofweek,
                "Month": date.month,
                "Week": date.isocalendar()[1],
                "WeekEnd": 1 if date.weekday() >= 5 else 0,
                "Lag_1": lag_1,
                "RollingMean_3": rolling,
                "UserCatAvg": user_cat_avg,
                "Category": category,
                "Campaign": campaign
            }
            pred = model.predict(pd.DataFrame([input_row]))[0]
            total_pred += pred

        results.append({
            "Category": int(category),
            "EstimatedSales": int(round(total_pred))
        })

    results.sort(key=lambda x: x["EstimatedSales"], reverse=True)
    return results[:3]


def predict_general_category_sales(start_date, end_date, model_path, data_path, campaign = 0):
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    df = pd.read_csv(data_path)
    df["Date"] = pd.to_datetime(df["Date"])

    date_ranges = pd.date_range(start=start_date, end=end_date)
    categories = df["Category"].unique()

    results = []
    for category in categories:
        kat_df = df[df["ProductCode"] == category].sort_values("Date")
        lag_1 = kat_df["SalesQuantity"].iloc[-1] if not kat_df.empty else 0
        rolling = kat_df["SalesQuantity"].tail(3).mean() if len(kat_df) >= 3 else lag_1
        user_cat_avg = kat_df["SalesQuantity"].mean() if not kat_df.empty else 0

        total_pred = 0
        for date in date_ranges:
            input_row = {
                "Day": date.dayofweek,
                "Month": date.month,
                "Week": date.isocalendar()[1],
                "WeekEnd": 1 if date.weekday() >= 5 else 0,
                "Lag_1": lag_1,
                "RollingMean_3": rolling,
                "UserCatAvg": user_cat_avg,
                "Category": category,
                "Campaign": campaign
            }
            pred = model.predict(pd.DataFrame([input_row]))[0]
            total_pred += pred

        results.append({
            "ProductCode": int(category),
            "EstimatedSales": int(round(total_pred))
        })

    results.sort(key=lambda x: x["EstimatedSales"], reverse=True)
    return results[:3]

