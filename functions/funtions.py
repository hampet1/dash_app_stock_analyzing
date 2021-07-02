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
    df_main = df["Adj Close"]
    return df_main


def get_data_2(ticker):
    """
    getting data in form of dataframe using yahoo finance
    data is in form of pandas dataframe with two columns data and closing price (close)
    """
    df2 = yf.download(ticker)
    df2 = df2["Adj Close"]
    return df2



def calculate_log_return(data):
    """
    we're using Monte Carlo method to predict
    possible stock prices in the future
    as a generator of random values we're using brownian motion

    input data is in form of pandas DataFrame datatype
    """

    # calculate log(Adj Close / Adj Close.shift(1)) - current_day/previous_day - to calculate rate of return, and times 100 because we can percentage
    log_return = np.log(1 + data.pct_change())*100
    return log_return


def mean_of_log_return(log_return):
    return log_return.mean()*100