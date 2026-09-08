"""JATS Section components sub-package.

Defines core structural components of JATS XML (Section, Appendix, GenericSection).
"""

from .Appendix import Appendix
from .AppendixGroup import AppendixGroup
from .GenericSection import GenericSection
from .Section import Section

__all__ = ["GenericSection", "Section", "Appendix", "AppendixGroup"]
