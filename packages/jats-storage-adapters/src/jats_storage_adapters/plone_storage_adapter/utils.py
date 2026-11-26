import hashlib
import hmac
import os
from urllib.parse import unquote, urlparse

LINK_SIGNING_KEY = os.environ.get("LINK_SIGNING_KEY")


def get_url_from_path(base_url: str, path: str) -> str:
    decoded_path = unquote(path)
    if ".." in decoded_path.split("/"):
        raise ValueError("Path must not contain parent directory references '..'")
    return f"{base_url}/{path.strip('/')}"


def get_path_from_url(base_url: str, url: str) -> str:
    base_path = urlparse(base_url).path.rstrip("/")
    result_path = urlparse(url).path
    if result_path.lower().startswith(base_path.lower()):
        return result_path[len(base_path) :]
    return result_path


def get_path_from_plone_object(base_url: str, obj: dict) -> str:
    obj_id = obj.get("@id", "")
    return get_path_from_url(base_url, obj_id)


def normalize_media_location(path: str, filename: str) -> tuple[str, str]:
    """Normalize the path and filename of a media file, so signing and URL building use the same values."""
    normalized_path = path.strip("/")
    normalized_filename = filename.strip("/")
    if ".." in f"{normalized_path}/{normalized_filename}".split("/"):
        raise ValueError("Media path must not contain parent directory references '..'")
    return normalized_path, normalized_filename


def sign_media(path: str, filename: str) -> tuple[str, str, str]:
    """Generate a signature for a media file based on its path and filename."""
    if LINK_SIGNING_KEY is None:
        raise ValueError("LINK_SIGNING_KEY environment variable is not set")

    normalized_path, normalized_filename = normalize_media_location(path, filename)
    message = f"{normalized_path}/{normalized_filename}".encode()
    signature = hmac.new(LINK_SIGNING_KEY.encode(), message, hashlib.sha256).hexdigest()
    return normalized_path, normalized_filename, signature


def verify_media_signature(path: str, filename: str, signature: str) -> tuple[str, str, bool]:
    """Verify the signature of a media file based on its path and filename."""
    normalized_path, normalized_filename, expected_signature = sign_media(path, filename)
    return normalized_path, normalized_filename, hmac.compare_digest(expected_signature, signature)
