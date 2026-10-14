import hashlib
import hmac
import os

LINK_SIGNING_KEY = os.environ.get("LINK_SIGNING_KEY")


def sign_media(path: str, filename: str) -> str:
    """Generate a signature for a media file based on its path and filename."""
    if LINK_SIGNING_KEY is None:
        raise ValueError("LINK_SIGNING_KEY environment variable is not set")

    message = f"{path}/{filename}".encode()
    return hmac.new(LINK_SIGNING_KEY.encode(), message, hashlib.sha256).hexdigest()


def verify_media_signature(path: str, filename: str, signature: str) -> bool:
    """Verify the signature of a media file based on its path and filename."""
    expected_signature = sign_media(path, filename)
    return hmac.compare_digest(expected_signature, signature)
