from datetime import date, datetime
from datetime import timezone as tz

import pandas as pd
from pandas._typing import (
    IntervalClosedType,
)


def monthly_date_range(start: date, end: date | None = None, inclusive: IntervalClosedType = "right") -> list[date]:
    if end is None:
        end = datetime.now(tz=tz.utc).date()
    return pd.date_range(start, end, freq="MS", inclusive=inclusive).date.tolist()


def list_download_file_date(start: date = date(2017, 1, 1), end: date | None = None) -> tuple[list[date], list[date]]:
    if end is None:
        end = datetime.now(tz=tz.utc).date()
    monthly_date = pd.date_range(start, end, freq="MS", inclusive="left").date.tolist()

    start = monthly_date[-1]
    monthly_date = monthly_date[:-1]

    daily_date = pd.date_range(start, end, freq="D", inclusive="left").date.tolist()

    return monthly_date, daily_date
