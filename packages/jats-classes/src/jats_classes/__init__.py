"""JATS Classes package.

Contains domain models and parser/converter logic for JATS XML entities.
"""

from .AppendixGroup import AppendixGroup
from .Article import Article
from .Back import Back
from .Body import Body
from .Document import JATSDocument
from .Front import Front
from .section import Appendix, GenericSection, Section

__all__ = [
    "JATSDocument",
    "Article",
    "Front",
    "Body",
    "Back",
    "AppendixGroup",
    "Section",
    "GenericSection",
    "Appendix",
]
