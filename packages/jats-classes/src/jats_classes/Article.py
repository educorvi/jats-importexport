"""JATS Article model.

Defines the structure of a complete JATS Article composed of Front, Body, and Back.
"""

from __future__ import annotations

from typing import Any

from lxml import etree

from .Back import Back
from .Body import Body
from .Front import Front


class Article:
    """Represents a complete JATS article element.

    An Article contains a Front (metadata), a Body (main text sections),
    and a Back (appendixes, references, notes).
    """

    front: Front
    body: Body
    back: Back

    def __init__(self, front: Front, body: Body, back: Back):
        """Initialize Article with front, body, and back components."""
        self.front = front
        self.body = body
        self.back = back

    @classmethod
    def from_xml_element(cls, article: etree._Element) -> Article:
        """Construct an Article from an lxml element representing a JATS <article>.

        Args:
            article: The lxml _Element node representing the <article> tag.

        Returns:
            An Article instance.
        """
        front_element = article.find("front")
        body_element = article.find("body")
        back_element = article.find("back")
        if front_element is None or body_element is None or back_element is None:
            raise ValueError(
                "Article element must contain 'front', 'body', and 'back' elements"
            )
        front = Front.from_xml_element(front_element)
        body = Body.from_xml_element(body_element)
        back = Back.from_xml_element(back_element)
        return cls(front=front, body=body, back=back)

    @classmethod
    def from_plone(cls, plone_article: Any) -> Article:
        """Construct an Article from a Plone article object listing components.

        Args:
            plone_article: A Plone article object.

        Returns:
            An Article instance.
        """
        if getattr(plone_article, "portal_type", None) != "Article":
            raise ValueError("Provided object is not an Article")
        front = body = back = None

        for element in plone_article.restrictedTraverse("contentlisting")():
            element = element.getObject()
            if getattr(element, "portal_type", None) == "Front":
                front = Front.from_plone(element)
            elif getattr(element, "portal_type", None) == "Body":
                body = Body.from_plone(element)
            elif getattr(element, "portal_type", None) == "Back":
                back = Back.from_plone(element)
        if not all([front, body, back]):
            raise ValueError("Article must contain Front, Body, and Back")
        assert front is not None and body is not None and back is not None
        return cls(front=front, body=body, back=back)
