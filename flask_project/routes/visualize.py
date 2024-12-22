import os
import pandas as pd
import plotly.express as px
from flask import Blueprint, request, jsonify, session

visualize_bp = Blueprint("visualize", __name__)

@visualize_bp.route("/", methods=["POST"], strict_slashes=False)
def visualize():
    print(f"Session at visualize: {session}")  # Debug print
    data = request.json
    x_column = data.get("x")
    y_column = data.get("y")

    if not x_column or not y_column:
        return jsonify({"error": "Both X and Y columns must be selected"}), 400

    try:
        file_path = session.get("uploaded_file")
        print("session",session)
        print("file_path",file_path)
        if not file_path or not os.path.exists(file_path):
            return jsonify({"error": f"File not found. Please upload again. " }), 400

        df = pd.read_csv(file_path)
        if x_column not in df.columns or y_column not in df.columns:
            return jsonify({"error": "Selected columns not found in the data"}), 400

        fig = px.line(df, x=x_column, y=y_column, title="Visualization")
        image_path = os.path.join("images", "visualization.png")
        fig.write_image(image_path)
        return jsonify({"image_url": f"/images/visualization.png"}), 200

    except Exception as e:
        print("error",session)

        return jsonify({"error": str(e)}), 500
