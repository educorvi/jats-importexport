"""Plone Upload Service implementation.

Provides functionality to upload files and create articles in a Plone CMS instance.
"""

import base64
import json
import logging
import mimetypes
import os
from typing import BinaryIO, cast

import httpx
from jats_classes import (
    AppendixGroup,
    Article,
    Back,
    Body,
    GenericSection,
    Section,
)
from jats_exporters import HtmlExporter
from lxml import etree, html
from lxml.html import HtmlElement

from ..interface import SaveJATSDocumentOptions

logger = logging.getLogger(__name__)


# vur workflow mapping
# status in jats -> plone transitions to convert the initial plone status (draft) to the desired status
WORKFLOW_MAPPING: dict[str, list[str]] = {
    "intern veröffentlicht": ["publish_internally"],
    "veröffentlicht": ["publish_internally"],  # yes, also internally published
    "Entwurf": [],
    "privat": ["make_private"],
}
DEFAULT_STATE: str = "Entwurf"

class PloneUploadService:
    """Service class for handling Plone file uploads and article creation."""
    base_url: str
    httpx_client: httpx.Client


    def __init__(self, base_url: str, httpx_client: httpx.Client):
        self.base_url = base_url
        self.httpx_client = httpx_client

    @staticmethod
    def __jats_status_to_plone_transitions(jats_status: str | None) -> list[str]:
        if jats_status is None or jats_status not in WORKFLOW_MAPPING:
            jats_status = DEFAULT_STATE
        return WORKFLOW_MAPPING.get(jats_status, [])

    def upload_file(self, file: BinaryIO, container: str) -> str:
        self.__create_container(container)

        filename = os.path.basename(getattr(file, "name", "") or "upload")

        content_type, _ = mimetypes.guess_type(filename)
        if content_type is None:
            content_type = "application/octet-stream"

        encoded = base64.b64encode(file.read()).decode("ascii")

        url = f"{self.base_url}/{container.strip('/')}"

        is_image = content_type.startswith("image/")
        portal_type = "Image" if is_image else "File"
        field_name = "image" if is_image else "file"

        response = self.httpx_client.post(
            url,
            json={
                "@type": portal_type,
                "title": filename,
                field_name: {
                    "data": encoded,
                    "encoding": "base64",
                    "filename": filename,
                    "content-type": content_type,
                },
            },
        )
        response.raise_for_status()

        return response.json().get("@id", url)

    def create_article(self, article: Article, container: str, options: SaveJATSDocumentOptions | None = None) -> str:
        """Create an Article root node and Front, Body, Back children in Plone."""
        self.__create_container(container)
        url = f"{self.base_url}/{container.strip('/')}"
        metadata = article.front.to_dict()
        if not metadata.get("title"):
            metadata["title"] = "Artikel"
        logger.debug(f"Creating article node in container: {url}")
        response = self.httpx_client.post(
            url,
            json={"@type": "Article", **metadata},
        )
        response.raise_for_status()

        result_url: str = response.json().get("@id")
        self.__create_body(article.body, result_url, options)
        self.__create_back(article.back, result_url)

        # set to workflow state derived from veroeffentlichungsstatus
        state = article.front.veroeffentlichungsstatus
        workflow_transitions = self.__jats_status_to_plone_transitions(state)
        for transition in workflow_transitions:
            transition_url = f"{response.json().get('@id')}/@workflow/{transition}"
            logger.debug(f"Applying workflow transition '{transition}' to article: {transition_url}")
            transition_response = self.httpx_client.post(transition_url, json={"include_children": "true"})
            transition_response.raise_for_status()

        return result_url

    def __create_container(self, container: str) -> None:
        """Recursively create folder structures ('Folder' type) in Plone if missing."""
        logger.debug(f"Creating container: {container}")
        parts = [p for p in container.strip("/").split("/") if p]
        current_path = ""

        for part in parts:
            current_path = f"{current_path}/{part}" if current_path else part
            url = f"{self.base_url}/{current_path}"

            response = self.httpx_client.get(url)
            if response.status_code == 200:
                continue
            if response.status_code != 404:
                response.raise_for_status()

            parent_url = f"{self.base_url}/{current_path.rsplit('/', 1)[0]}" if "/" in current_path else self.base_url
            response = self.httpx_client.post(parent_url, json={"@type": "Folder", "title": part, "id": part})
            response.raise_for_status()

    def __create_body(self, body: Body, container_url: str, options: SaveJATSDocumentOptions | None = None) -> str:
        """Create a Body node inside a Plone Article and upload its sections."""
        logger.debug(f"Creating body node for article: {container_url}")
        response = self.httpx_client.post(
            container_url,
            json={
                "@type": "Body",
                "title": "Textkörper",
            },
        )
        response.raise_for_status()
        response_url: str = response.json().get("@id")

        if options and options.get("use_html_sections"):
            # check if the first section is the table of contents (always create as normal section)
            # TODO: This is a temporary workaround. Ideally, the TOC should be handled in a more robust way.
            sections_start_index = 0
            if len(body.sections) > 0:
                first_section = body.sections[0]
                if first_section.title and first_section.title.lower() == "inhaltsverzeichnis":
                    self.__create_section(first_section, response_url)
                    sections_start_index = 1
            for section in body.sections[sections_start_index:]:
                self.__create_easy_section(section, response_url)
        else:
            for section in body.sections:
                self.__create_section(section, response_url)
        return response_url

    def __create_back(self, back: Back | None, container_url: str) -> str | None:
        """Create a Back node inside a Plone Article and upload its appendix groups."""
        if back is None:
            return None
        logger.debug(f"Creating back node for article: {container_url}")
        response = self.httpx_client.post(
            container_url,
            json={
                "@type": "Back",
                "title": "Anhang",
            },
        )
        response.raise_for_status()
        response_url: str = response.json().get("@id")
        for app in back.appendix_groups:
            self.__create_appendix_group(app, response_url)
        return response_url

    def __create_appendix_group(self, app_group: AppendixGroup, container_url: str) -> str:
        """Create an AppendixGroup node inside Plone Back and upload sections."""
        logger.debug(f"Creating appendix group node for article: {container_url}")
        response = self.httpx_client.post(
            container_url,
            json={
                "@type": "AppendixGroup",
                "title": app_group.title or "Anhanggruppe",
                "label": app_group.label,
                "label_title_raw": app_group.label_title_raw,
                "content_raw": app_group.content_raw,
            },
        )
        response.raise_for_status()
        response_url: str = response.json().get("@id")
        for app in app_group.appendixes:
            self.__create_section(app, response_url)
        return response_url

    def __create_section(self, section: GenericSection, container_url: str) -> str:
        """Recursively create a Section/Appendix node structure in a Plone container."""
        portal_type: str
        if isinstance(section, Section):
            portal_type = "Section"
        else:
            portal_type = "Appendix"

        title = section.title or "JATS-Abschnitt"

        logger.debug(f"Creating section node for article: {container_url}")
        logger.debug(f"Section title: {json.dumps(title)}")
        response = self.httpx_client.post(
            container_url,
            json={
                "@type": portal_type,
                "title": title,
                "sec_type": section.sec_type,
                "label": section.label,
                "label_title_raw": section.label_title_raw,
                "content_raw": section.content_raw,
            },
        )
        response.raise_for_status()
        response_url: str = response.json().get("@id")
        for sub_section in section.sections:
            self.__create_section(sub_section, response_url)
        return response_url

    def __create_easy_section(self, section: GenericSection, container_url: str) -> str:
        """Create an EasySection node in Plone with HTML content.
        Uses the HTML exporter to convert JATS content to HTML for storage in Plone.
        """
        html_exporter = HtmlExporter()
        label, title, html_content = self.__transform_section_to_easy_section(section, html_exporter)
        if title is None:
            title = "HTML-Abschnitt"

        logger.debug(f"Creating easy section node for article: {container_url}")
        logger.debug(f"EasySection title: {json.dumps(title)}")

        json_data = {
            "@type": "EasySection",
            "title": title,
            "label": label,
            "content": html_content,
        }

        response = self.httpx_client.post(container_url, json=json_data)
        response.raise_for_status()
        response_url: str = response.json().get("@id")
        return response_url

    def __transform_section_to_easy_section(
        self, section: GenericSection, html_exporter: HtmlExporter, level: int = 3
    ) -> tuple[str | None, str | None, str]:
        """Recursively transform a Section instance to an EasySection representation."""
        label = section.label
        title = section.title
        xml_content = section.content_raw
        html_content = html_exporter.transform_xml(xml_content) if xml_content else ""
        if html_content:
            html_content = self.__sanitize_html_for_richtext(html_content)

        for child in section.sections:
            child_label, child_title, child_content = self.__transform_section_to_easy_section(
                child, html_exporter, level + 1
            )
            heading_tag = f"h{min(level, 6)}"
            if child_title:
                if child_label:
                    heading = f"{child_label} {child_title}"
                else:
                    heading = child_title
                html_content += f"<{heading_tag}>{heading}</{heading_tag}>"
            html_content += child_content

        return label, title, html_content

    def __sanitize_html_for_richtext(self, html_content: str) -> str:
        """Sanitize HTML content of an easy section for Plone richtext fields."""
        tree = html.fromstring(html_content, parser=html.HTMLParser(recover=True, remove_comments=True))
        tree = cast(HtmlElement, tree)

        # remove <a> tags that have no content and only an id attribute
        empty_a_tags = tree.xpath("//a[not(*) and normalize-space(.) = '' and @id and count(@*) = 1]")
        if isinstance(empty_a_tags, list):
            for a in empty_a_tags:
                a.drop_tag()

        # remove <div> tags but keep their content
        etree.strip_tags(tree, "div")

        # wrap <img> in <picture> tags
        imgs = tree.xpath("//img")
        if isinstance(imgs, list):
            for img in imgs:
                parent = img.getparent()
                label = None
                label_element = None
                title = None
                title_element = None

                # Look at preceding siblings for optional caption elements
                prev = img.getprevious()
                if prev is not None and prev.tag == "h3" and "title" in prev.get("class", "").split():
                    title = prev.text_content().strip()
                    title_element = prev
                    prev = prev.getprevious()
                if prev is not None and prev.tag == "h5" and "label" in prev.get("class", "").split():
                    label = prev.text_content().strip()
                    label_element = prev

                # Create new structure
                p = etree.Element("p")

                if label or title:
                    figure = etree.SubElement(
                        p, "figure", attrib={"class": "image-richtext picture-variant-medium captioned"}
                    )

                    picture = etree.SubElement(figure, "picture", attrib={"class": "captioned"})

                    _ = etree.SubElement(picture, "img", attrib={"alt": img.get("alt", ""), "src": img.get("src", "")})

                    caption = etree.SubElement(figure, "figcaption", attrib={"class": "image-caption"})
                    caption.text = f"{label or ''} {title or ''}".strip()

                else:
                    picture = etree.SubElement(p, "picture")

                    _ = etree.SubElement(
                        picture,
                        "img",
                        attrib={
                            "alt": img.get("alt", ""),
                            "class": "image-richtext picture-variant-medium",
                            "src": img.get("src", ""),
                        },
                    )

                # Replace img with new structure
                parent.replace(img, p)

                # Remove consumed caption elements
                if label_element is not None:
                    label_element.drop_tree()

                if title_element is not None:
                    title_element.drop_tree()

        return etree.tostring(tree, encoding="unicode", method="html", pretty_print=True)
