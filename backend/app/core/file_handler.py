import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_book_image(file):
    if not file or not allowed_file(file.filename):
        raise ValueError("Invalid file type or no file selected.")

    # Create a secure, unique filename
    filename = secure_filename(file.filename)
    extension = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4()}.{extension}"

    # Save the file
    upload_folder = current_app.config['UPLOAD_FOLDER']
    save_path = os.path.join(upload_folder, unique_filename)
    file.save(save_path)

    # Return the public-facing path
    return f"/uploads/{unique_filename}"