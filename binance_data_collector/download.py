from collections.abc import Iterable
from datetime import date
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from binance_data_collector import s3
from binance_data_collector.utils import monthly_date_range

binance_kline_headers = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "count",
    "taker_buy_volume",
    "taker_buy_quote_volume",
    "ignore",
]
metrics_headers = [
    "create_time",
    "symbol",
    "sum_open_interest",
    "sum_open_interest_value",
    "count_toptrader_long_short_ratio",
    "sum_toptrader_long_short_ratio",
    "count_long_short_ratio",
    "sum_taker_long_short_vol_ratio",
]

headers_mapping = {
    "klines": binance_kline_headers,
    "indexPriceKlines": binance_kline_headers,
    "markPriceKlines": binance_kline_headers,
    "premiumIndexKlines": binance_kline_headers,
    "metrics": metrics_headers,
}


def download_klines_df(
    symbol: str,
    interval: str | None = None,
    trading_type: str = "spot",
    market_data_type: str = "klines",
    *,
    data_dir: Path = Path("data"),
    force: bool = False,
):
    out_path = download_klines(
        symbol=symbol,
        interval=interval,
        trading_type=trading_type,
        market_data_type=market_data_type,
        data_dir=data_dir,
        force=force,
    )
    df = pd.read_csv(out_path, index_col=0)
    try:
        df.index = pd.to_datetime(df.index, unit="ms")
    except ValueError:
        df.index = pd.to_datetime(df.index)
    return df


def download_klines(
    symbol: str,
    interval: str | None = None,
    trading_type: str = "spot",
    market_data_type: str = "klines",
    *,
    data_dir: Path = Path("data"),
    force: bool = False,
) -> Path:
    out_path = data_dir / Path(f"{symbol}-{interval}-{trading_type}-{market_data_type}.csv")

    if out_path.exists() and not force:
        return out_path

    # download zip files from s3
    zip_files = _download_s3(
        symbol=symbol, interval=interval, trading_type=trading_type, market_data_type=market_data_type
    )

    # extract file
    csv_files = _extract_zip_files(zip_files)

    # combine all files
    headers = headers_mapping[market_data_type]
    return _combine_csv_files(csv_files, out_path=out_path, headers=headers)


def _download_s3(symbol: str, interval: str | None, trading_type: str, market_data_type: str) -> Iterable[Path]:
    """Download zip files from s3."""
    monthly_prefix = s3.get_path(
        trading_type=trading_type,
        time_period="monthly",
        market_data_type=market_data_type,
        symbol=symbol,
        interval=interval,
    )
    s3.sync(prefix=monthly_prefix, include="*.zip")

    daily_prefix = s3.get_path(
        trading_type=trading_type,
        time_period="daily",
        market_data_type=market_data_type,
        symbol=symbol,
        interval=interval,
    )

    # TODO: if no monthly files, download daily files
    if x := list(Path(monthly_prefix).glob("*.zip")):
        latest_monthly_file = max(x)

        _, _, year, month = latest_monthly_file.stem.split("-")

        ms = monthly_date_range(start=date(int(year), int(month), 1))

        for m in ms:
            s3.sync(prefix=daily_prefix, include=f"*{m:%Y-%m}*.zip")
    else:
        s3.sync(prefix=daily_prefix, include="*.zip")

    # TODO: glob only downloaded files
    zip_pattern = (
        s3.get_path(
            trading_type=trading_type,
            time_period="*",
            market_data_type=market_data_type,
            symbol=symbol,
            interval=interval,
        )
        + "*.zip"
    )

    return Path.cwd().glob(zip_pattern)


def _extract_zip_files(zip_files: Iterable[Path]) -> Iterable[Path]:
    """Extract zip files."""

    for i in zip_files:
        with ZipFile(i, "r") as f:
            f.extractall(i.parent)
        yield i.parent / Path(i.stem).with_suffix(".csv")


def _combine_csv_files(csv_files: Iterable[Path], out_path: Path, headers: list[str]) -> Path:
    """Combine csv files in a directory into one csv file."""
    header_line = ",".join(headers) + "\n"
    with open(out_path, "w") as outfile:
        outfile.write(header_line)
        for i in sorted(csv_files, key=lambda x: x.stem):
            with open(i) as infile:
                # Before 2022-06 (BTCUSDT-15m-2022-06.csv), the csv files don't have header
                if (x := infile.readline()) != header_line:
                    outfile.write(x)
                outfile.write(infile.read())
    return out_path
