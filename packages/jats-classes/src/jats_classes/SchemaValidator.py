
import pathlib
from functools import cache, lru_cache
from typing import Any

import xmlschema
from xmlschema.validators import XsdComplexType, XsdElement, XsdGroup


class SchemaValidator:
    """Utility class for validating XML against the JATS schema."""

    @staticmethod
    @cache
    def get_schema() -> xmlschema.XMLSchema:
        """Return the cached XMLSchema object for the JATS schema."""
        xsd_path = pathlib.Path(__file__).parent / "schema" / "dguv_jats.xsd"
        return xmlschema.XMLSchema(str(xsd_path))

    @staticmethod
    @lru_cache(maxsize=128)
    def allows_direct_child(parent_tag: str, target_tag: str) -> bool:
        """
        Return True if target_tag can occur as a direct child of parent_tag according to the schema.

        Handles:
            - xs:element
            - xs:element ref="..."
            - xs:group ref="..."
            - sequence / choice / all
        """
        def check(particle: XsdGroup | XsdElement | Any) -> bool:
            # <xsd:element ...>
            # resolves ref automatically if present
            if isinstance(particle, XsdElement):
                return particle.name == target_tag

            # <xsd:group ref="...">
            if isinstance(particle, XsdGroup) and particle.ref is not None:
                return check(particle.ref)

            # <xsd:sequence>, <xsd:choice>, <xsd:all>
            if isinstance(particle, XsdGroup):
                return any(check(child) for child in particle)

            return False

        schema = SchemaValidator.get_schema()
        parent_element = schema.elements.get(parent_tag)
        if parent_element is None:
            return False
        if not isinstance(parent_element.type, XsdComplexType):
            return False
        return check(parent_element.type.content)
