"""Interface definitions for JATS document exporters.

Defines the abstract base Exporter class that all format-specific
exporters must inherit from and implement.
"""

import abc

from jats_classes import JATSDocument


class Exporter[T](metaclass=abc.ABCMeta):
    """Base class for exporters, providing an interface for exporting data."""

    @abc.abstractmethod
    def export(self, document: JATSDocument) -> T:
        """Export the provided data using the exporter's implementation."""
        raise NotImplementedError
