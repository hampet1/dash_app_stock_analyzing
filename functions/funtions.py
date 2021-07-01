import yfinance as yf
import numpy as np
from scipy.stats import norm
from datetime import date
import pandas as pd
from pandas_datareader import data as wb






def get_data(ticker):
    """
    getting data in form of dataframe using yahoo finance
    data is in form of pandas dataframe with two columns data and closing price (close)
    """
    df = yf.download(ticker)
    df.reset_index(inplace=True)
    df = df[["Date", "Adj Close"]]
    return df