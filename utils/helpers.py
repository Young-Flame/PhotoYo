import os
from werkzeug.utils import secure_filename
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """Generate a unique filename with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    return timestamp + secure_filename(filename)

def format_datetime(dt):
    """Format datetime to a readable string."""
    return dt.strftime('%B %d, %Y at %I:%M %p')

def get_file_size(filepath):
    """Get file size in human readable format."""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def truncate_text(text, length=100):
    """Truncate text to specified length with ellipsis."""
    if len(text) <= length:
        return text
    return text[:length].rstrip() + '...'
