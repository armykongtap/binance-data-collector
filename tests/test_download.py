import pandas as pd
import pytest

from binance_data_collector.download import download_klines


@pytest.mark.parametrize("symbol", ["BTCUSDT", "ETHUSDT"])
@pytest.mark.parametrize("interval", ["15m", "1h", "1d"])
@pytest.mark.parametrize("trading_type", ["spot", "um", "cm"])
# @pytest.mark.parametrize(
#     "market_data_type", ["klines", "indexPriceKlines", "markPriceKlines", "premiumIndexKlines", "metrics"]
# )
def test_download_klines(symbol: str, interval: str, trading_type: str, market_data_type: str = "klines"):
    csv_file = download_klines(
        symbol=symbol, interval=interval, trading_type=trading_type, market_data_type=market_data_type
    )

    df = pd.read_csv(csv_file, index_col=0)

    assert df.index.is_unique
    assert df.index.is_monotonic_increasing
