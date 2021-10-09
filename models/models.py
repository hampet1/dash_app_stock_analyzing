import pandas as pd
from statsmodels.tsa.arima_model import ARIMA



def arma_model(train, type_of_model, days_forecast):
    """
    by default only second degree order (order = 2) in order to make it easier for the users

    """
    order_AR = 0
    order_MA = 0


    if type_of_model == 'AR':
        order_AR = 2
    elif type_of_model == 'MA':
        order_MA = 2
    elif type_of_model == 'ARMA':
        order_AR = 2
        order_MA = 2
    else:
        return "wrong data type or wrong term, the only correct arguments are AR, MA or ARMA"

    model_arma = ARIMA(train['Log return'], order=(order_AR, 0, order_MA))
    results_ar = model_arma.fit()
    # forecasting
    pred = results_ar.forecast(days_forecast)

    predictions = pred[0]
    # lower bound for all tree predictions
    lower_bound = pred[2][:, 0]
    # upper bound for all tree prediction
    upper_bound = pred[2][:, 1]
    # todays date
    today_date = str(train.index[-1].year) + '-' + str(train.index[-1].month) + '-' + str(train.index[-1].day)
    # future predicted business dates

    s = pd.date_range(today_date, periods=days_forecast + 1, freq='b')[1:]

    df = pd.DataFrame(predictions, columns=['Log return'], index=s)
    output_data = train[['Log return']]
    output_data = output_data.append(df, ignore_index=False)

    return output_data

