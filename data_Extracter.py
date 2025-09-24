# get_gold.py
# Python 3.9+
# Install required packages:
# pip install yfinance pandas pandas_datareader requests beautifulsoup4 lxml

import os
import pandas as pd
import datetime as dt

# --- Function 1: Yahoo Finance (futures / market quotes) via yfinance ---
def fetch_gold_yahoo(ticker="GC=F", start="1960-01-01", end=None):
    """
    Fetches historical data from Yahoo Finance (yfinance).
    Note: futures data availability may be limited depending on the contract history.
    """
    import yfinance as yf
    if end is None:
        end = dt.datetime.today().strftime("%Y-%m-%d")
    yf_ticker = yf.Ticker(ticker)
    df = yf_ticker.history(start=start, end=end, interval="1d", actions=False)
    # Keep only adjusted close (or Close if Adj Close missing)
    if "Adj Close" in df.columns:
        series = df[["Adj Close"]].rename(columns={"Adj Close": "price"})
    else:
        series = df[["Close"]].rename(columns={"Close": "price"})
    series.index = pd.to_datetime(series.index)
    return series

# --- Function 2: FRED (St. Louis Fed) using pandas_datareader ---
def fetch_gold_fred(series_id="GOLDPMGBD228NLBM", start="1968-01-01", end=None):
    """
    Fetches the FRED series. Common IDs:
      - GOLDPMGBD228NLBM : Gold Fixing Price 3:00 P.M. (London) (daily)
      - GOLDAMGBD228NLBM : Gold Fixing Price 10:30 A.M. (London) (daily)
    FRED series typically go back to 1968 (daily LBMA-type fixes).
    """
    from pandas_datareader import data as pdr
    if end is None:
        end = dt.datetime.today().strftime("%Y-%m-%d")
    df = pdr.DataReader(series_id, "fred", start, end)
    df = df.rename(columns={series_id: "price"})
    df.index = pd.to_datetime(df.index)
    return df

# --- Function 3: MacroTrends (annual / long-term table scraping) ---
def fetch_gold_macrotrends(annual=True):
    """
    Scrapes MacroTrends historical gold price table.
    MacroTrends provides long-run annual/monthly data (good for long spans back to 1900s).
    This function returns a DataFrame of annual prices (Year, Price USD/oz).
    """
    import requests
    from bs4 import BeautifulSoup

    if annual:
        url = "https://www.macrotrends.net/assets/php/timeseries_ajax.php?type=gold-price&freq=annual"
    else:
        url = "https://www.macrotrends.net/assets/php/timeseries_ajax.php?type=gold-price&freq=monthly"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    # macrotrends returns JSON-ish HTML fragment where first column is date and second col price
    data = r.json()
    # data is list of [date_str, value_str]
    df = pd.DataFrame(data, columns=["date", "price"])
    # convert date to year or month
    df["date"] = pd.to_datetime(df["date"])
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.set_index("date").sort_index()
    return df

# --- Utility: save to CSV ---
def save_df(df, filename="gold_prices.csv"):
    df.to_csv(filename, index=True)
    print(f"Saved {len(df)} rows to {filename}")

# --- Example usage ---
if __name__ == "__main__":
    # 1) Try FRED daily LBMA-style price (best daily series back to 1968)
    try:
        print("Fetching FRED daily LBMA-style gold PM price (from 1968)...")
        fred_df = fetch_gold_fred(series_id="GOLDPMGBD228NLBM")
        print("FRED rows:", len(fred_df))
        save_df(fred_df, "gold_fred_pm.csv")
    except Exception as e:
        print("FRED fetch failed:", e)

    # 2) Yahoo Finance (futures) - might be limited historically
    try:
        print("Fetching Yahoo Finance GC=F (futures)...")
        yahoo_df = fetch_gold_yahoo("GC=F", start="1970-01-01")  # start can be adjusted
        print("Yahoo rows:", len(yahoo_df))
        save_df(yahoo_df, "gold_yahoo_gc_f.csv")
    except Exception as e:
        print("Yahoo fetch failed:", e)

    # 3) MacroTrends annual (very long history, good for 1900s -> present)
    try:
        print("Fetching MacroTrends annual gold prices...")
        macro_df = fetch_gold_macrotrends(annual=True)
        print("MacroTrends rows:", len(macro_df))
        save_df(macro_df, "gold_macrotrends_annual.csv")
    except Exception as e:
        print("MacroTrends fetch failed:", e)
