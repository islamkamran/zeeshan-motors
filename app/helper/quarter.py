from datetime import datetime, timedelta

# Helper function to get date range based on quarter
def get_date_range(quarter: str):
    year = datetime.now().year
    if quarter == "first_quarter":
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 3, 31)
    elif quarter == "second_quarter":
        start_date = datetime(year, 4, 1)
        end_date = datetime(year, 6, 30)
    elif quarter == "third_quarter":
        start_date = datetime(year, 7, 1)
        end_date = datetime(year, 9, 30)
    elif quarter == "fourth_quarter":
        start_date = datetime(year, 10, 1)
        end_date = datetime(year, 12, 31)
    elif quarter == "biannual":
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 6, 30)
    elif quarter == "annual":
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
    else:
        raise ValueError("Invalid quarter specified")
    return start_date, end_date