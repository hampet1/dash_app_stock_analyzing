import yfinance as yf
import numpy as np
from bs4 import BeautifulSoup
import requests
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


def calculate_log_return(data):
    """
    log return - calculate return of investment
    """

    # calculate log(Adj Close / Adj Close.shift(1)) - current_day/previous_day - to calculate rate of return, and times 100 because we can percentage
    log_return = np.log(1 + data.pct_change())*100
    return log_return


def mean_of_log_return(log_return):
    return log_return.mean()*100


def top_ten_active_stocks():
    """
    scrape top 10 active stocks from yahoo.com/most-active
    use the values for our dropdown menu in side bar
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}
    url = 'https://finance.yahoo.com/most-active/'
    response = requests.get(url, headers=headers)
    top_ten = []
    soup = BeautifulSoup(response.content, 'lxml')
    counter = 0
    for item in soup.select('.simpTblRow'):
        if counter < 10:
            ticker = item.select('[aria-label=Symbol]')[0].get_text()
            name = item.select('[aria-label=Name]')[0].get_text()
            top_ten.append({'label': name, 'value': ticker})
        counter += 1
    return top_ten


