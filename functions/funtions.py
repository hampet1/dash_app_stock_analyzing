from bs4 import BeautifulSoup
import numpy as np
import requests
import yfinance as yf

from dash.exceptions import PreventUpdate


def top_ten_active_stocks():
    """
    scrape top 10 active stocks from yahoo.com/most-active
    use the values for our dropdown menu in side bar
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) '
                      'Version/9.0.2 Safari/601.3.9'}
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


def get_data(ticker):
    """
    getting data in form of dataframe using yahoo finance
    data is in form of pandas dataframe with two columns data and closing price (close)
    """
    try:
        df = yf.download(ticker)
        # renaming in order to plotly convention for labeling axis (a bit tricky to implement column name with space)
        df = df.rename(columns={"Adj Close": "Adj_Close"})
        df = df["Adj_Close"]
        df = df.asfreq('b')
        df = df.fillna(method='ffill')
        return df
    except Exception:
        raise PreventUpdate


def log_return(data):
    """
    log return - calculate return of investment
    plus 1 + to make the percentage result clearer
    """
    return np.log(1 + data.pct_change()) * 100


def log(data):
    """
    just log prices while it goes to the ARIMA - with integrated order 1
    """
    return np.log(data)


def mean_log_return(log_ret):
    return round(log_ret.tail(30).mean(), 2)


def risk_of_return(log_ret):
    return round(log_ret.tail(30).std(), 2)
