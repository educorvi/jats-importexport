"""Plone Modify Service implementation.

Provides functionality to modify existing files and articles in a Plone CMS instance.
"""

import logging

import httpx

logger = logging.getLogger(__name__)

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
        if not related_articles_ids:
            return False
        related_items = [  # save already linked articles, so they are not overwritten
            ra if isinstance(ra, str) else ra.get("@id")
            for ra in data.get("relatedItems", [])
            if (ra if isinstance(ra, str) else ra.get("@id"))
        ]
        for related_id in list(related_articles_ids):  # iterate over copy to allow removal during iteration
            query = [
                {"i": "portal_type", "o": "plone.app.querystring.operation.selection.any", "v": ["Article"]},
                {"i": "article_id", "o": "plone.app.querystring.operation.string.is", "v": related_id},
            ]
            search_response = self.httpx_client.post(f"{self.base_url}/@querystring-search", json={"query": query})
            search_response.raise_for_status()
            search_results = search_response.json().get("items", [])
            if search_results:
                related_items.extend([res.get("@id") for res in search_results if res.get("@id")])
                related_articles_ids.remove(related_id)
        if related_items:
            update_response = self.httpx_client.patch(
                article_url,
                json={"relatedItems": related_items, "related_articles": related_articles_ids},
                headers={"Content-Type": "application/json"},
            )
            update_response.raise_for_status()
            return True
        return False
