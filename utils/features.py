def create_input_features(date, lag_1=0, rolling_mean=0, user_id=None, prod_category=None, user_cat_avg=0, campaign=0):
    return {
        "Day": date.dayofweek,
        "Month": date.month,
        "Week": date.isocalendar()[1],
        "WeekEnd": 1 if date.weekday() >= 5 else 0,
        "Lag_1": lag_1,
        "RollingMean_3": rolling_mean,
        "UserID": user_id,
        "Category": prod_category,
        "UserCatAvg": user_cat_avg,
        "Campaign": campaign
    }