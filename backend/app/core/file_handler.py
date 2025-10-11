"""
Provides utility functions for handling file uploads, such as book images.
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Checks if a file's extension is in the list of allowed types."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_book_image(file):
    """
    Saves an uploaded book image with a secure, unique filename.
    Returns the public URL path to the saved image.
    """
    if not file or not allowed_file(file.filename):
        raise ValueError("Invalid file type or no file selected.")

    # Create a secure and unique filename to prevent conflicts and path traversal attacks.
    filename = secure_filename(file.filename)
    extension = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4()}.{extension}"

    # Save the file to the configured upload folder.
    upload_folder = current_app.config['UPLOAD_FOLDER']
    save_path = os.path.join(upload_folder, unique_filename)
    file.save(save_path)

    # Return the public-facing URL path.
    return f"/uploads/{unique_filename}"