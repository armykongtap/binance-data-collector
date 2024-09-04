from datetime import date

from binance_data_collector.utils import monthly_date_range


def test_monthly_date_range():
    start = date(2017, 1, 1)
    end = date(2017, 3, 2)

    actual = monthly_date_range(start, end)

    assert actual == [date(2017, 2, 1), date(2017, 3, 1)]
