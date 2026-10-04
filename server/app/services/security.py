import os
import re
from pathlib import Path
from typing import List, Optional

def sanitize_filename(filename: str) -> str:
    """
    Remove directory traversal attempts, slashes, and hazardous characters from filename.
    """
    base = os.path.basename(filename)
    # Remove leading dots to prevent hidden files or traversal tricks
    base = base.lstrip(".")
    # Replace characters not alphanumeric, dash, underscore, dot
    sanitized = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', base)
    if not sanitized:
        sanitized = "unnamed_video.mp4"
    return sanitized

def validate_path_safety(target_dir: Path, file_path: Path) -> bool:
    """
    Ensure the resolved file_path is strictly within target_dir.
    """
    try:
        resolved_target = target_dir.resolve()
        resolved_file = file_path.resolve()
        return resolved_file == resolved_target or resolved_target in resolved_file.parents
    except Exception:
        return False
