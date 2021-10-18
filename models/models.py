import pandas as pd
import statsmodels.tsa.arima.model as stats


def arma_model(train, type_of_model, days_forecast):
    """
    by default only second degree order (order = 2) in order to make it easier for the users
    we're appending forecasted values to original values
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
        # we are not using any model - so just return input data
        output_data = train[["Adj_Close"]]
        return output_data

    if days_forecast > 0:
        # integrated 1
        model_arma = stats.ARIMA(train, order=(order_AR, 1, order_MA))
        results_ar = model_arma.fit()
        # forecasting
        pred = results_ar.forecast(days_forecast)

        df = pd.DataFrame(pred)
        df = df.rename(columns={"predicted_mean": "Adj_Close"})

        output_data = train[["Adj_Close"]]
        output_data = output_data.append(df, ignore_index=False)

        return output_data
