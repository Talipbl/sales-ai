from datetime import datetime

CAMPAIGN_PERIODS = [
    ("2023-11-25", "2023-11-30"),
    ("2023-12-20", "2023-12-31"),
    ("2024-02-10", "2024-02-14"),
]

def is_campaign_exists(tarih: datetime) -> int:
    for start_date, end_date in CAMPAIGN_PERIODS:
        if datetime.strptime(start_date, "%Y-%m-%d") <= tarih <= datetime.strptime(end_date, "%Y-%m-%d"):
            return 1
    return 0