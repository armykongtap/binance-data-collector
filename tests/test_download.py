import pandas as pd
import pytest

from binance_data_collector.download import _is_header, download_klines


@pytest.mark.parametrize(
    "symbol, interval, trading_type, market_data_type",
    [
        # BTCUSDT spot klines
        ("BTCUSDT", "15m", "spot", "klines"),
        ("BTCUSDT", "1h", "spot", "klines"),
        ("BTCUSDT", "1d", "spot", "klines"),
        # ETHUSDT spot klines
        ("ETHUSDT", "15m", "spot", "klines"),
        ("ETHUSDT", "1h", "spot", "klines"),
        ("ETHUSDT", "1d", "spot", "klines"),
        # BTCUSDT um klines
        ("BTCUSDT", "15m", "um", "klines"),
        ("BTCUSDT", "1h", "um", "klines"),
        ("BTCUSDT", "1d", "um", "klines"),
        # ETHUSDT um klines
        ("ETHUSDT", "15m", "um", "klines"),
        ("ETHUSDT", "1h", "um", "klines"),
        ("ETHUSDT", "1d", "um", "klines"),
        # BTCUSDT spot premiumIndexKlines
        ("BTCUSDT", "15m", "um", "premiumIndexKlines"),
        ("BTCUSDT", "1h", "um", "premiumIndexKlines"),
        ("BTCUSDT", "1d", "um", "premiumIndexKlines"),
        # ETHUSDT spot premiumIndexKlines
        ("ETHUSDT", "15m", "um", "premiumIndexKlines"),
        ("ETHUSDT", "1h", "um", "premiumIndexKlines"),
        ("ETHUSDT", "1d", "um", "premiumIndexKlines"),
    ],
)
def test_download_klines(symbol: str, interval: str, trading_type: str, market_data_type: str):
    csv_file = download_klines(
        symbol=symbol, interval=interval, trading_type=trading_type, market_data_type=market_data_type, force=True
    )

    df = pd.read_csv(csv_file, index_col=0, header=None)

    assert not df.empty
    assert df.index.is_unique
    assert df.index.is_monotonic_increasing
    if interval == "1d" and market_data_type == "klines":
        assert _is_same_step(df.index)


def _is_same_step(series: pd.Series | pd.Index) -> bool:
    v = series.diff().value_counts()  # type: ignore
    return v.shape[0] == 1


@pytest.mark.parametrize(
    "line,expected",
    [
        (
            "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore",
            True,
        ),
        ("1719792000000,-0.00012914,0.00227583,-0.00116705,-0.00030565,0,1719878399999,0,17279,0,0,0", False),
    ],
)
def test_is_header(line: str, expected: bool):
    actual = _is_header(line)
    assert actual == expected
