from flask_project.tests.test_utils import cleanup_upload_folder
import pytest
from flask_project.app import app
from flask import session
import os
import tempfile
import re

def remove_last_underscore_before_dot(filename):
    # Use regex to find the last underscore before the dot
    name = re.sub(r'_(?=[^_]*\.)', '', filename, count=1)
    new_filename = re.sub(r'(T)([^/]+)', r'\1_\2', name, count=1)
    return new_filename

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["UPLOAD_FOLDER"] = "/Users/seyednavidmirnourilangeroudi/timeSeries/flask_project/uploads"
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    client = app.test_client()
    yield client

def create_test_csv(content):
    """Create a temporary CSV file for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".csv")
    temp_file.write(content)
    temp_file.close()
    # print(temp_file.name)
    # print(remove_last_underscore_before_dot(temp_file.name.replace("/","_")[1:]))
    return temp_file.name

def setup_mock_session(client, data):
    with client.session_transaction() as session:
        session.update(data)

def test_visualize_with_mock_session(client):
    """Test visualization functionality with mocked session."""
    sample_csv = "x,value\n1,10\n2,20\n3,30"
    test_file_path = create_test_csv(sample_csv)
    with open(test_file_path, "rb") as test_file:
        upload_response = client.post("/upload", data={"file": test_file}, content_type="multipart/form-data")
    # os.remove(test_file_path)  # Clean up the temporary file

    assert upload_response.status_code == 200

    uploaded_file_path = app.config["UPLOAD_FOLDER"] + "/" + remove_last_underscore_before_dot(test_file_path.replace("/","_")[1:])
    print("uploaded_file_path",uploaded_file_path)
    setup_mock_session(client, {"uploaded_file": uploaded_file_path})

    response = client.post(
        "/visualize",
        json={"x": "x", "y": "value"},
        content_type="application/json",
    )
    print(response.data)

    assert response.status_code == 200

def test_forecast_with_mock_session(client):
    """Test forecast functionality with mocked session."""
    sample_csv = "x,value\n1,10\n2,20\n3,30"
    test_file_path = create_test_csv(sample_csv)
    with open(test_file_path, "rb") as test_file:
        upload_response = client.post("/upload", data={"file": test_file}, content_type="multipart/form-data")
    # os.remove(test_file_path)  # Clean up the temporary file

    assert upload_response.status_code == 200

    uploaded_file_path = app.config["UPLOAD_FOLDER"] + "/" + remove_last_underscore_before_dot(test_file_path.replace("/","_")[1:])
    setup_mock_session(client, {"uploaded_file": uploaded_file_path})

    response = client.post(
        "/forecast",
        json={"x": "x", "y": "value"},
        content_type="application/json",
    )
    cleanup_upload_folder(app.config["UPLOAD_FOLDER"])
    assert response.status_code == 200
