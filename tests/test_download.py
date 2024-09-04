import pandas as pd

from binance_data_collector.download import download_klines


def test_download_klines():
    csv_file = download_klines(symbol="BTCUSDT", interval="1h")

    df = pd.read_csv(csv_file, index_col=0)

    assert df.index.is_unique
    assert df.index.is_monotonic_increasing
