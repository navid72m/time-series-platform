from flask import Blueprint, request, jsonify, session, make_response
import pandas as pd
import os
from flask_project.utils.forecasting import (
    generate_arima_forecast,
    generate_prophet_forecast,
    generate_holt_winters_forecast
)

forecast_bp = Blueprint("forecast", __name__)


# Handle preflight OPTIONS requests
# @forecast_bp.route("/", methods=["OPTIONS"])
# def forecast_options():
#     response = make_response()
#     response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"  # Adjust for your frontend's URL
#     response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
#     response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
#     response.headers["Access-Control-Allow-Credentials"] = "true"
#     return response, 200

@forecast_bp.route("/", methods=["POST"])
def forecast():
    data = request.json
    y_column = data.get("y")
    x_column = data.get("x")
    model = data.get("model", "ARIMA").upper()  # Default to ARIMA if no model provided

    if not y_column:
        return jsonify({"error": "Y column must be selected"}), 400

    try:
        file_path = session.get("uploaded_file")
        if not file_path or not os.path.exists(file_path):
            return jsonify({"error": "File not found. Please upload again."}), 400

        df = pd.read_csv(file_path)
        if y_column not in df.columns:
            return jsonify({"error": f"Column {y_column} not found in the data"}), 400

        # Call the appropriate forecasting function
        if model == "ARIMA":
            image_path = generate_arima_forecast(df, y_column)
        elif model == "PROPHET":
            image_path = generate_prophet_forecast(df, x_column,y_column)
        elif model == "HOLT-WINTERS":
            image_path = generate_holt_winters_forecast(df, y_column)
        else:
            return jsonify({"error": "Invalid model selected"}), 400

        response = jsonify({"image_url": f"/images/{image_path}"})
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response, 200

    except Exception as e: 
        response = jsonify({"error": str(e)})
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return jsonify({"error": str(e)}), 500

