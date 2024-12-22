import os
import io
from werkzeug.datastructures import FileStorage


def create_test_csv(data: str, filename: str = "test.csv") -> FileStorage:
    """
    Create an in-memory CSV file for testing.
    
    Args:
        data (str): The content of the CSV as a string.
        filename (str): The filename for the in-memory file.

    Returns:
        FileStorage: An in-memory file object suitable for Flask test clients.
    """
    return FileStorage(
        stream=io.BytesIO(data.encode("utf-8")),
        filename=filename,
        content_type="text/csv",
    )


# def setup_mock_session(client, session_data: dict):
#     """
#     Set up mock session data for Flask testing.

#     Args:
#         client: The Flask test client.
#         session_data (dict): Key-value pairs to set in the session.
#     """
#     with client.session_transaction() as session:
#         for key, value in session_data.items():
#             session[key] = value


def cleanup_upload_folder(folder_path: str):
    """
    Clean up files in the upload folder after tests.

    Args:
        folder_path (str): Path to the upload folder.
    """
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
