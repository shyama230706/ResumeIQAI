import os

# Project folders
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

# Create uploads folder automatically if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = [".pdf"]

# Maximum upload size (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024