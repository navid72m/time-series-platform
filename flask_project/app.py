from flask import Flask , session, jsonify, request, session, make_response
from flask_cors import CORS
from flask_project.routes.upload import upload_bp
from flask_project.routes.visualize import visualize_bp
# from flask_project.routes.forecast import forecast_bp
from flask_project.routes.forecast import forecast_bp
from flask_session import Session
from datetime import timedelta


app = Flask(__name__)

# Configure server-side session
app.config["SESSION_TYPE"] = "filesystem"  # Stores session data on the server filesystem
app.config["SESSION_PERMANENT"] = True    # Optional: set to False if sessions should expire after browser close
app.config["SESSION_FILE_DIR"] = "./.flask_session"  # Specify a directory for session files
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)  # Session valid for 7 days

Session(app)
# Initialize Flask app

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['IMAGE_FOLDER'] = 'images'
app.secret_key = 'your_secret_key'

# Enable CORS
CORS(app,resources={r"/*": {"origins": "http://localhost:3000"}},supports_credentials=True)

# Register Blueprints
app.register_blueprint(upload_bp, url_prefix="/upload")
app.register_blueprint(visualize_bp, url_prefix="/visualize")
app.register_blueprint(forecast_bp, url_prefix="/forecast")

@app.before_request
def log_session_id():
    print(f"Session ID: {request.cookies.get('session')}")
    print(f"Session Data: {session}")

from flask import send_from_directory

@app.route("/images/<path:image_path>", methods=["GET"])
def get_image(image_path):
    try:
        # Use `send_from_directory` to serve images securely
        return send_from_directory(app.config["IMAGE_FOLDER"], image_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 404


# @app.after_request
# def add_cors_headers(response):
#     response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")  # Allow frontend domain
#     response.headers.add("Access-Control-Allow-Credentials", "true")  # For session/cookies
#     response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
#     response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
#     return response

@app.route("/test", methods=["GET", "POST", "OPTIONS"])
def test():
    if request.method == "OPTIONS":
        return make_response("", 204)  # Handle preflight OPTIONS request
    return jsonify({"message": "CORS is working!"})

if __name__ == "__main__":
    app.run(debug=True)
