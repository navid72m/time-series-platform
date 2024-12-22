import os
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import plotly.graph_objects as go

def generate_arima_forecast(df, y_column, steps=50):
    import os
    import plotly.graph_objects as go
    from statsmodels.tsa.arima.model import ARIMA
    import pandas as pd

    # Drop NaNs and select the relevant column
    df = df[[y_column]].dropna()

    # Train ARIMA model
    model = ARIMA(df[y_column], order=(5, 1, 0))
    model_fit = model.fit()

    # Generate forecast
    forecast = model_fit.forecast(steps=steps)
    forecast_index = pd.RangeIndex(start=df.index[-1] + 1, stop=df.index[-1] + 1 + steps, step=1)

    # Create forecast series with proper indices
    forecast_series = pd.Series(forecast, index=forecast_index)

    # Combine historical data and forecast for plotting
    combined_series = pd.concat([df[y_column], forecast_series])

    # Plotting
    fig = go.Figure()

    # Historical plot
    fig.add_trace(
        go.Scatter(
            x=combined_series.index[:len(df)],
            y=combined_series[:len(df)],
            mode="lines",
            name="Historical",
            line=dict(color="blue"),
        )
    )

    # Forecast plot
    fig.add_trace(
        go.Scatter(
            x=forecast_series.index,
            y=forecast_series,
            mode="lines",
            name="Forecast",
            line=dict(color="orange"),
        )
    )

    # Save the plot
    image_path = "forecast.png"
    fig.write_image(os.path.join("images", image_path))
    return image_path


from prophet import Prophet
import plotly.graph_objects as go
import os
import pandas as pd
def generate_prophet_forecast(df,x_column, y_column, steps=15):
    # Ensure the dataframe contains the required columns
    print(df)
    if y_column not in df.columns:
        raise ValueError(f"The column '{y_column}' does not exist in the dataframe.")

    # Prepare the data for Prophet
    df = df[[x_column,y_column]].dropna()
    df.reset_index(inplace=True)  # Reset index to make the index a regular column
    df.rename(columns={ y_column: "y"}, inplace=True)
    df.rename(columns={x_column: "ds"}, inplace=True)
    print(df)
    # Ensure 'ds' column is datetime and resample yearly
    # try:
    #     df['ds'] = pd.to_datetime(df['ds'], errors='coerce')
    #     print(df)
    # except Exception as e:
    #     print("Error parsing dates:", e)
    #     raise

    # Drop rows with invalid dates
    # df.dropna(subset=['ds'], inplace=True)
    # print(df)

    if df.empty:
        raise ValueError("No valid dates found in the data. Check the 'ds' column for invalid entries.")

    # Resample to yearly frequency (if data is not already yearly)
    # df = df.resample('Y', on='ds').mean().reset_index()
    # df = df.resample('Y', on='ds').mean().interpolate().reset_index()
    print(df)

    # Handle cases with too few rows
    if len(df) < 2:
        raise ValueError("Dataframe has less than 2 non-NaN rows after resampling.")

    # Ensure 'ds' column is datetime
    try:
        df['ds'] = pd.to_datetime(df['ds'], errors='coerce', format='%Y')
    except Exception as e:
        print("Error parsing dates:", e)
        raise
    
    print("dfff")
    print(df)
    # Train the Prophet model
    model = Prophet()
    model.fit(df)

    # Generate future dataframe for the next 50 years
    # future = model.make_future_dataframe(periods=steps, freq='Y')
    try:
        start_date = df['ds'].max()
        future_dates = [start_date + pd.DateOffset(years=i) for i in range(1, steps + 1)]
        future_df = pd.DataFrame({'ds': future_dates})  
        print("future_df")
        print(future_df)
    except Exception as e:
        print("Error generating future dates:", e)
        raise
    try:
        forecast = model.predict(future_df)
    except Exception as e:
        print("Error generating forecast:", e)
        raise
    print("forecast")
    print(forecast)
    # Plot the historical and forecast data
    fig = go.Figure()
    forecast["y"] = forecast["yhat"]  # Rename yhat to y for consistency
    forecast_combined = pd.concat([df[["ds", "y"]], forecast[["ds", "y"]]], ignore_index=True)

    print("combined_df")
    print(forecast_combined)
    # print(combined_df[len(df):])
    # Historical data
    fig.add_trace(
        go.Scatter(
            x=forecast_combined["ds"][:len(df)],  # Historical part
            y=forecast_combined["y"][:len(df)],
            mode="lines",
            name="Historical",
            line=dict(color="blue"),
        )
    )

    # Forecast data
    fig.add_trace(
        go.Scatter(
            # x=forecast_combined["ds"][len(df):],  # Forecast part
            y=forecast_combined["y"][len(df):],
            mode="lines",
            name="Forecast",
            line=dict(color="orange"),
        )
    )

    # Adding confidence intervals for the forecast
    # fig.add_trace(
    #     go.Scatter(
    #         x=forecast["ds"],
    #         y=forecast["yhat_upper"],
    #         mode="lines",
    #         name="Upper Confidence Interval",
    #         line=dict(color="green", dash="dot")
    #     )
    # )
    # fig.add_trace(
    #     go.Scatter(
    #         x=forecast["ds"],
    #         y=forecast["yhat_lower"],
    #         mode="lines",
    #         name="Lower Confidence Interval",
    #         line=dict(color="red", dash="dot")
    #     )
    # )

    # Save the plot
    image_path = "prophet_forecast_yearly.png"
    os.makedirs("images", exist_ok=True)  # Ensure the images directory exists
    fig.write_image(os.path.join("images", image_path))

    return image_path



from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pandas as pd
import plotly.graph_objects as go
import os

def generate_holt_winters_forecast(df, y_column, steps=50):
    df = df[[y_column]].dropna()
    model = ExponentialSmoothing(df[y_column], seasonal='add', seasonal_periods=12)
    model_fit = model.fit()

    forecast = model_fit.forecast(steps)

    # Plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=df[y_column], mode="lines", name="Historical"))
    fig.add_trace(go.Scatter(y=forecast, mode="lines", name="Forecast", line=dict(color="orange")))

    image_path = "holt_winters_forecast.png"
    fig.write_image(os.path.join("images", image_path))
    return image_path
