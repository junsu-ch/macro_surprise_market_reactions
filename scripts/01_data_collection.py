import pandas as pd
import yfinance as yf
from pandas_datareader import data as web

from _paths import PROCESSED_DIR, ensure_project_directories


START_DATE = "2015-01-01"
END_DATE = pd.Timestamp.today().strftime("%Y-%m-%d")

FRED_SERIES = {
    "dgs2": "DGS2",
    "dgs10": "DGS10",
    "usdjpy": "DEXJPUS",
}

YFINANCE_TICKERS = {
    "spy": "SPY",
    "qqq": "QQQ",
    "tlt": "TLT",
}


def download_fred_series(series_map: dict[str, str], start: str, end: str) -> pd.DataFrame:
    frames = []

    for column_name, fred_code in series_map.items():
        series = web.DataReader(fred_code, "fred", start, end)
        series = series.rename(columns={fred_code: column_name})
        frames.append(series)

    data = pd.concat(frames, axis=1)
    data.index.name = "date"

    return data


def download_yfinance_prices(tickers: dict[str, str], start: str, end: str) -> pd.DataFrame:
    price_frames = []

    for column_name, ticker in tickers.items():
        data = yf.download(
            ticker,
            start=start,
            end=end,
            auto_adjust=True,
            progress=False,
        )

        if data.empty:
            raise ValueError(f"No data downloaded for {ticker}.")

        if isinstance(data.columns, pd.MultiIndex):
            close = data["Close"][ticker].rename(column_name)
        else:
            close = data["Close"].rename(column_name)

        price_frames.append(close)
        print(f"{ticker}: {close.notna().sum()} observations")

    prices = pd.concat(price_frames, axis=1)
    prices.index.name = "date"

    return prices


def main() -> None:
    ensure_project_directories()

    price_data = download_yfinance_prices(YFINANCE_TICKERS, START_DATE, END_DATE)
    fred_data = download_fred_series(FRED_SERIES, START_DATE, END_DATE)

    market_data = price_data.join(fred_data, how="outer").sort_index()
    market_data["yield_curve_10y2y"] = market_data["dgs10"] - market_data["dgs2"]

    market_columns = [
        "spy",
        "qqq",
        "tlt",
        "usdjpy",
        "dgs2",
        "dgs10",
        "yield_curve_10y2y",
    ]

    market_data = market_data[market_columns]

    market_path = PROCESSED_DIR / "market_data.csv"
    market_data.to_csv(market_path)

    print(f"Saved market data to: {market_path}")
    print(market_data.tail())


if __name__ == "__main__":
    main()
