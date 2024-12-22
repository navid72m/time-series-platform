import pandas as pd
import requests
import plotly.express as px
from statsmodels.tsa.arima.model import ARIMA
from flask import Flask, request, jsonify, render_template, session
import os

# Initialize Flask App
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route: Homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route: Upload CSV
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully', 'file_path': filepath}), 200

# Route: Fetch from API
@app.route('/fetch_api', methods=['POST'])
def fetch_api():
    data = request.json
    api_url = data.get('api_url')
    headers = data.get('headers', {})

    if not api_url:
        return jsonify({'error': 'API URL is required'}), 400

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch data from API'}), 400

    return jsonify({'data': response.json()}), 200

# Route: Visualize Data
@app.route('/visualize', methods=['POST'])
def visualize():
    data = request.json
    df = pd.DataFrame(data)

    if 'date' not in df.columns or 'value' not in df.columns:
        return jsonify({'error': 'Data must have "date" and "value" columns'}), 400

    df['date'] = pd.to_datetime(df['date'])
    fig = px.line(df, x='date', y='value', title='Historical Data')
    fig_html = fig.to_html()

    return jsonify({'plot': fig_html}), 200

# Route: Forecast Data
@app.route('/forecast', methods=['POST'])
def forecast():
    data = request.json
    df = pd.DataFrame(data)

    if 'date' not in df.columns or 'value' not in df.columns:
        return jsonify({'error': 'Data must have "date" and "value" columns'}), 400

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df.asfreq('D')  # Ensure daily frequency
    df['value'] = df['value'].interpolate()  # Fill missing values

    # Train ARIMA model
    model = ARIMA(df['value'], order=(5, 1, 0))
    model_fit = model.fit()

    # Forecast the next 30 days
    forecast = model_fit.forecast(steps=30)
    future_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=30)

    forecast_df = pd.DataFrame({'date': future_dates, 'forecast': forecast})

    # Create plot
    fig = px.line(title='Forecast vs Historical')
    fig.add_scatter(x=df.index, y=df['value'], mode='lines', name='Historical')
    fig.add_scatter(x=forecast_df['date'], y=forecast_df['forecast'], mode='lines', name='Forecast')
    fig_html = fig.to_html()

    return jsonify({'forecast_plot': fig_html}), 200


@app.before_request
def make_session_permanent():
    session.permanent = True


if __name__ == '__main__':
    app.run(debug=True)
