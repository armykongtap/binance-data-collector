import os

import boto3

# Initialize a session using your specific region
s3 = boto3.client("s3", region_name="ap-northeast-1")

# Specify the bucket name
BUCKET_NAME = "data.binance.vision"


def list_objects(prefix: str = "", suffix: str = "") -> list[str]:
    """List objects in the bucket with the specified prefix."""
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

    return [i["Key"] for i in response["Contents"] if i["Key"].endswith(suffix)]


def sync(prefix: str = "", include: str = ""):
    """Sync files from S3 to local directory."""
    cmd = f"aws s3 sync s3://{BUCKET_NAME}/{prefix} {prefix}"
    if include:
        cmd += f' --exclude "*" --include "{include}"'
    os.system(cmd)  # noqa: S605


# https://github.com/binance/binance-public-data/blob/master/python/utility.py#L105
def get_path(trading_type: str, time_period: str, market_data_type: str, symbol: str, interval: str | None = None):
    """Get the path for the given parameters.

    Args:
        trading_type (str): Trading type (spot or um or cm).
        time_period (str): Time period (daily or monthly).
        market_data_type (str): Market data type (klines).
        symbol (str): Symbol (e.g. BTCUSDT).
        interval (str, optional): Interval (e.g. 15m). Defaults to None.
    """
    trading_type_path = "data/spot"
    if trading_type != "spot":
        trading_type_path = f"data/futures/{trading_type}"
    if interval is not None:
        path = f"{trading_type_path}/{time_period}/{market_data_type}/{symbol.upper()}/{interval}/"
    else:
        path = f"{trading_type_path}/{time_period}/{market_data_type}/{symbol.upper()}/"
    return path
