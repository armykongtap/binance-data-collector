from datetime import date
from pathlib import Path
from zipfile import ZipFile

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


def download_klines(
    symbol: str,
    interval: str | None = None,
    trading_type: str = "spot",
    market_data_type: str = "klines",
) -> Path:
    out_path = Path(f"data/{symbol}-{interval}-{trading_type}-{market_data_type}.csv")

    if out_path.exists():
        return out_path

    # download zip files
    zip_files = _download_klines(
        symbol=symbol, interval=interval, trading_type=trading_type, market_data_type=market_data_type
    )

    # extract file
    csv_files = _extract_zip_files(zip_files)

    # combine all files
    return _combine_csv_files(csv_files, out_path=out_path)


def _download_klines(symbol: str, interval: str | None, trading_type: str, market_data_type: str) -> list[Path]:
    # download zip files
    monthly_prefix = s3.get_path(
        trading_type=trading_type,
        time_period="monthly",
        market_data_type=market_data_type,
        symbol=symbol,
        interval=interval,
    )
    s3.sync(prefix=monthly_prefix, include="*.zip")

    latest_monthly_file = max(Path(monthly_prefix).glob("*.zip"))

    _, _, year, month = latest_monthly_file.stem.split("-")

    daily_prefix = s3.get_path(
        trading_type=trading_type,
        time_period="daily",
        market_data_type=market_data_type,
        symbol=symbol,
        interval=interval,
    )
    ms = monthly_date_range(start=date(int(year), int(month), 1))
    for m in ms:
        s3.sync(prefix=daily_prefix, include=f"*{m:%Y-%m}*.zip")

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

    return list(Path.cwd().glob(zip_pattern))


def _extract_zip_files(zip_files: list[Path]) -> list[Path]:
    """Extract zip files."""

    def _inner(i):
        with ZipFile(i, "r") as f:
            f.extractall(i.parent)
        return i.parent / Path(i.stem).with_suffix(".csv")

    return [_inner(i) for i in zip_files]


def _combine_csv_files(csv_files: list[Path], out_path: Path) -> Path:
    """Combine csv files in a directory into one csv file."""

    with open(out_path, "w") as outfile:
        # TODO: find a way to get the header from the file
        outfile.write(",".join(binance_kline_headers) + "\n")
        for i in sorted(csv_files, key=lambda x: x.stem):
            with open(i) as f:
                # Check header because before 2022-06 (BTCUSDT-15m-2022-06.csv), the csv files don't have header
                first_line = f.readline().strip()
                if not first_line.isalpha():
                    # If the first line doesn't match, write it to the output file
                    outfile.write(first_line + "\n")

                # Write the remaining lines of the current CSV file to the output file
                for line in f:
                    outfile.write(line)

    return out_path
