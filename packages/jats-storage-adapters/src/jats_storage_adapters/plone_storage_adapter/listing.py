"""Plone List Service implementation.

Provides functionality to list articles and metadata from a Plone CMS instance.
"""

import logging

import httpx

logger = logging.getLogger(__name__)


class PloneListingService:
    """Service class for handling listing of articles and metadata from a Plone CMS instance."""

    base_url: str
    httpx_client: httpx.Client

    def __init__(self, base_url: str, httpx_client: httpx.Client):
        self.base_url = base_url
        self.httpx_client = httpx_client

    def list_metadata_contents(self, meta: str) -> list[str]:
        url = f"/@faceted-search?portal_type=Article&facets={meta}&facets_only=1"
        response = self.httpx_client.get(url)
        response.raise_for_status()
        facets = response.json().get("facets", {}).get(meta, {}).get("items", [])
        values = list(map(lambda item: item.get("value", ""), facets))
        return values

    def list_article_items(
        self,
        fachbereiche: list[str] | None = None,
        sachgebiete: list[str] | None = None,
        organisationseinheiten: list[str] | None = None,
        rubriken: list[str] | None = None,
        batch_start: int = 0,
        batch_size: int | None = None,
    ) -> tuple[list[dict], int]:
        url = f"{self.base_url}/@querystring-search"
        query = [{"i": "portal_type", "o": "plone.app.querystring.operation.selection.any", "v": ["Article"]}]
        if fachbereiche:
            query.append({"i": "fachbereich", "o": "plone.app.querystring.operation.selection.any", "v": fachbereiche})
        if sachgebiete:
            query.append({"i": "sachgebiet", "o": "plone.app.querystring.operation.selection.any", "v": sachgebiete})
        if organisationseinheiten:
            query.append(
                {
                    "i": "organisationseinheit",
                    "o": "plone.app.querystring.operation.selection.any",
                    "v": organisationseinheiten,
                }
            )
        if rubriken:
            query.append({"i": "journal_title", "o": "plone.app.querystring.operation.selection.any", "v": rubriken})
        search: dict = {"query": query, "b_start": batch_start}
        if batch_size is not None:
            search["b_size"] = batch_size
        response = self.httpx_client.post(url, json=search)
        response.raise_for_status()
        json_res = response.json()
        items = json_res.get("items", [])
        while batch_size is None and json_res.get("batching", {}).get("next"):
            next_url = json_res["batching"]["next"]
            response = self.httpx_client.post(next_url, json=search)
            response.raise_for_status()
            json_res = response.json()
            items.extend(json_res.get("items", []))
        return items, json_res.get("items_total", len(items))
