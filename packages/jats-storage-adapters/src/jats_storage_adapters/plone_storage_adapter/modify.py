"""Plone Modify Service implementation.

Provides functionality to modify existing files and articles in a Plone CMS instance.
"""

import logging
import re
from pathlib import PurePosixPath
from typing import cast
from urllib.parse import urlsplit, urlunsplit

import httpx
from jats_classes import (
    Appendix,
    AppendixGroup,
    Article,
    Back,
    Body,
    Section,
)

logger = logging.getLogger(__name__)

XLINK_HREF_PATTERN = re.compile(r"xlink:href\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)


class PloneModifyService:
    """Service class for handling modifications to existing files and articles in a Plone CMS instance."""

    base_url: str
    httpx_client: httpx.Client

    def __init__(self, base_url: str, httpx_client: httpx.Client):
        self.base_url = base_url
        self.httpx_client = httpx_client

    def link_related_articles(self, article_url: str) -> bool:
        """Link related articles for one article

        Returns True if the article had related articles linked and was updated, False otherwise."""
        response = self.httpx_client.get(article_url)
        response.raise_for_status()
        data = response.json()

        related_articles_ids = data.get("related_articles", [])
        related_articles_translations_ids = data.get("related_articles_translations", [])
        if not related_articles_ids and not related_articles_translations_ids:
            return False

        related_items = [  # save already linked articles, so they are not overwritten
            ra if isinstance(ra, str) else ra.get("@id")
            for ra in data.get("relatedItems", [])
            if (ra if isinstance(ra, str) else ra.get("@id"))
        ]
        related_items_translations = [  # save already linked translated articles, so they are not overwritten
            ra if isinstance(ra, str) else ra.get("@id")
            for ra in data.get("related_items_translations", [])
            if (ra if isinstance(ra, str) else ra.get("@id"))
        ]

        modified_1 = False
        if related_articles_ids:
            related_articles_ids, related_items, modified_1 = self.__link_related_articles_update_lists(
                related_articles_ids, related_items
            )
        modified_2 = False
        if related_articles_translations_ids:
            related_articles_translations_ids, related_items_translations, modified_2 = (
                self.__link_related_articles_update_lists(related_articles_translations_ids, related_items_translations)
            )

        if modified_1 or modified_2:
            update_response = self.httpx_client.patch(
                article_url,
                json={
                    "relatedItems": related_items,
                    "related_items_translations": related_items_translations,
                    "related_articles": related_articles_ids,
                    "related_articles_translations": related_articles_translations_ids,
                },
                headers={"Content-Type": "application/json"},
            )
            update_response.raise_for_status()
            return True
        return False

    def __link_related_articles_update_lists(
        self, related_articles_ids: list[str], related_articles_items: list[str]
    ) -> tuple[list[str], list[str], bool]:
        """Search for related articles and update the lists of related article IDs and items.

        Args:
            related_articles_ids (list[str]): A list of related article IDs.
            related_articles_items (list[str]): A list of related article items already linked.

        Returns:
            tuple[list[str], list[str], bool]: A tuple containing the updated list of related article IDs,
            the updated list of related article items, and a boolean indicating if any modifications were made.
        """
        modified = False
        for related_id in list(related_articles_ids):  # iterate over copy to allow removal during iteration
            query = [
                {"i": "portal_type", "o": "plone.app.querystring.operation.selection.any", "v": ["Article"]},
                {"i": "webcode", "o": "plone.app.querystring.operation.string.is", "v": related_id},
            ]
            search_response = self.httpx_client.post(f"{self.base_url}/@querystring-search", json={"query": query})
            search_response.raise_for_status()
            search_results = search_response.json().get("items", [])
            if search_results:
                related_articles_items.extend([res.get("@id") for res in search_results if res.get("@id")])
                related_articles_ids.remove(related_id)
                modified = True
        return related_articles_ids, related_articles_items, modified

    def delete_article(self, article_url: str, article: Article) -> list[str]:
        """Deletes an Article including all referenced assets and child items.

        Args:
            article_url (str): The URL of the article to delete.
            article (Article): The Article object to delete.

        Returns:
            list[str]: A list of error messages for any failed deletions, or an empty list if all deletions succeeded.
        """
        assets = self._find_assets_paths(article)
        containers = self._get_assets_container_urls(assets)
        errors = []
        for asset_url in assets:
            error = self._delete_resource(asset_url)
            if error:
                errors.append(error)
        for container_url in containers:
            if not self._assets_container_is_empty(container_url):
                continue
            error = self._delete_resource(container_url)
            if error:
                errors.append(error)
        self._delete_resource(article_url, raise_on_error=True)
        return errors

    def _find_assets_paths(self, container: Article | Body | Back | AppendixGroup | Appendix | Section) -> list[str]:
        """Finds all asset paths (xlink:href values) referenced in the raw content of the given structure.

        Recursively walks the article body and back sections and collects all ``xlink:href`` values
        found in the ``content_raw`` of every Section, Appendix, and AppendixGroup.

        Args:
            container: The article or section to search for assets.

        Returns:
            list[str]: A list of asset paths (absolute urls) found in the container.
        """
        asset_paths = set()
        if isinstance(container, Article):
            asset_paths.update(self._find_assets_paths(container.body))
            if container.back:
                asset_paths.update(self._find_assets_paths(container.back))
        elif isinstance(container, Body):
            for section in container.sections:
                asset_paths.update(self._find_assets_paths(section))
        elif isinstance(container, Back):
            for appendix_group in container.appendix_groups:
                asset_paths.update(self._find_assets_paths(appendix_group))
        elif isinstance(container, AppendixGroup):
            for appendix in container.appendixes:
                asset_paths.update(self._find_assets_paths(appendix))
        elif isinstance(container, Appendix):
            for section in container.sections:
                asset_paths.update(self._find_assets_paths(cast(Section, section)))
        elif isinstance(container, Section):
            for section in container.sections:
                asset_paths.update(self._find_assets_paths(cast(Section, section)))

        if isinstance(container, Section) or isinstance(container, Appendix) or isinstance(container, AppendixGroup):
            if container.content_raw:
                for href_value in XLINK_HREF_PATTERN.findall(container.content_raw):
                    if not href_value or not isinstance(href_value, str) or href_value.startswith("#"):
                        continue

                    parsed = urlsplit(href_value)
                    if parsed.scheme or parsed.netloc:
                        base_netloc = urlsplit(self.base_url).netloc
                        if parsed.scheme in ("http", "https") and parsed.netloc == base_netloc:
                            asset_paths.add(self._strip_image_alias(href_value))

        return list(asset_paths)

    def _strip_image_alias(self, url: str) -> str:
        """Strip a Plone image scaling alias (e.g. ``/@@images/image-600-...``) from an asset URL.

        URLs such as ``http://localhost:8080/Plone1/images/example.jpeg/@@images/image-600-....jpeg``
        are reduced to the base object URL ``http://localhost:8080/Plone1/images/example.jpeg``.
        """
        return url.split("@@images", 1)[0].rstrip("/")

    def _get_assets_container_urls(self, asset_paths: list[str]) -> list[str]:
        """Derive the set of all containers (parent URLs) of the given asset URLs.

        Each asset URL is reduced to its container URL, i.e. the URL with the file name (last path
        segment) stripped. The base URL itself is excluded, so assets stored directly under the base
        URL do not yield the base URL as a container.

        Args:
            asset_paths: A list of asset URLs (as returned by ``_find_assets_paths``).

        Returns:
            list[str]: The list of container URLs of all given assets.
        """
        base_segments = [s for s in PurePosixPath(urlsplit(self.base_url).path or "/").parts if s != "/"]
        containers: set[str] = set()
        for asset_url in asset_paths:
            parsed = urlsplit(asset_url)
            segments = [s for s in PurePosixPath(parsed.path or "/").parts if s != "/"]
            if len(segments) < 2:
                # File sits directly in the root (no parent directory); nothing to containerize
                continue

            parent_segments = segments[:-1]
            if parent_segments == base_segments:
                # Container is the base URL itself; skip it
                continue

            parent_path = "/" + "/".join(parent_segments)
            containers.add(urlunsplit((parsed.scheme, parsed.netloc, parent_path, parsed.query, "")))
        return list(containers)

    def _assets_container_is_empty(self, container_url: str) -> bool:
        """Check if the given assets container URL is empty.

        Args:
            container_url: The URL of the container to check.

        Returns:
            bool: True if the container is empty, False otherwise.
        """
        response = self.httpx_client.get(container_url)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            return False
        data = response.json()
        return len(data.get("items", [])) == 0

    def _delete_resource(self, url: str, raise_on_error: bool = False) -> str | None:
        """Delete the resource at the given URL.

        Args:
            url: The URL of the resource to delete.

        Returns:
            str | None: None on success, the error message on failure.
        """
        response = self.httpx_client.delete(url)
        try:
            response.raise_for_status()
            return None
        except httpx.HTTPStatusError as e:
            if raise_on_error:
                raise
            return str(e)
