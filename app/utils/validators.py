import os
from flask import current_app
from werkzeug.utils import secure_filename
from typing import List, Optional, Any

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def validate_input(text: Optional[str] = None, file: Any = None) -> List[str]:
    errors = []

    # Text validation
    if text:
        if len(text) > 100000:
            errors.append("Text too long (max 100,000 characters).")

    # File validation
    if file:
        if not allowed_file(file.filename):
            errors.append("Invalid file type. Only .txt and .epub are allowed.")

        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        if size > current_app.config['MAX_CONTENT_LENGTH']:
            errors.append(f"File too large. Max size is {current_app.config['MAX_CONTENT_LENGTH']/(1024*1024)}MB.")

    return errors
