import os
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from flask_project.utils.helpers import allowed_file
from pandas import read_csv

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/", methods=["POST"], strict_slashes=False)
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join("uploads", filename)
        file.save(file_path)
        session['uploaded_file'] = file_path
        session.modified = True
        print("session",session)
        # print("file_111path",file_path)
        # print("hi")
        try:
            df = read_csv(file_path)
            columns = df.columns.tolist()
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify({"message": "File uploaded successfully", "file_path": file_path, "columns": columns}), 200
        # return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200

    return jsonify({"error": "Invalid file type"}), 400


@upload_bp.route('/test_session', methods=['GET', 'POST'])
def test_session():
    if 'count' in session:
        session['count'] += 1
    else:
        session['count'] = 1
    return jsonify({"count": session['count']})
