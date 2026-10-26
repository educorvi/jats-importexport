import abc
from collections.abc import Callable


class JATSClassInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def to_xml(self) -> str:
        """Serialize the JATS class instance back to its XML representation."""
        raise NotImplementedError

    @abc.abstractmethod
    def replace_media_links(
        self,
        media_link_conversion: Callable[[str, tuple[bytes, str] | None], str],
        media_downloader: Callable[[str], tuple[bytes, str]] | None = None,
    ) -> dict[str, tuple[str, tuple[bytes, str] | None]]:
        """Replace media links in the document using the provided conversion function.

        Args:
            media_link_conversion: A callable that takes the original media URL and an optional
                tuple of (bytes, str) representing the downloaded media content and mimetype,
                and returns the new media URL.
            media_downloader: An optional callable to download media content given a URL.
            return_media_info: If True, return a dictionary of media URLs to their downloaded content.

        Returns:
            A dictionary mapping old media links to a tuple of (new media link, downloaded content as bytes and
            mimetype) or None if no media_downloader is provided or return_media_info is False.
        """
        raise NotImplementedError
