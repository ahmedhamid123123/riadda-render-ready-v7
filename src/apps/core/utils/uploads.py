from typing import Optional, Tuple

# Default allowed MIME types for images
DEFAULT_ALLOWED_IMAGE_MIME = {"image/png", "image/jpeg", "image/svg+xml"}
DEFAULT_MAX_IMAGE_BYTES = 2 * 1024 * 1024  # 2 MB


def validate_uploaded_image(file_obj, *, allowed_mime: Optional[set] = None, max_bytes: Optional[int] = None) -> Tuple[bool, Optional[str]]:
    """Validate an uploaded image-like file.

    Returns (True, None) if valid, otherwise (False, error_message).
    Does not raise; callers can decide how to handle errors.
    """
    if file_obj is None:
        return True, None

    if allowed_mime is None:
        allowed_mime = DEFAULT_ALLOWED_IMAGE_MIME
    if max_bytes is None:
        max_bytes = DEFAULT_MAX_IMAGE_BYTES

    size = getattr(file_obj, "size", None)
    if size is not None and size > max_bytes:
        return False, f"File too large (max {max_bytes} bytes)"

    content_type = getattr(file_obj, "content_type", "")
    if content_type and content_type not in allowed_mime:
        return False, "Invalid file type"

    return True, None
