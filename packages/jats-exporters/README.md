# jats-exporters

Export [`jats-classes`](../jats-classes) documents to different output formats.

## Exporters

### JATS XML — `JatsExporter`

Serializes a `JATSDocument` back to a valid JATS XML string.

```python
from jats_exporters.jats import JatsExporter

xml: str = JatsExporter().export(document)
```

### HTML — `HtmlExporter` / `HtmlExporterStandalone`

Converts a `JATSDocument` to HTML via an XSLT stylesheet.
`HtmlExporterStandalone` produces a self-contained HTML page.

```python
from jats_exporters.html import HtmlExporter, HtmlExporterStandalone

html: str = HtmlExporter().export(document)
```

### PDF — `PdfExporter`

Renders documents with WeasyPrint. MathML formulas are typeset locally as
embedded SVG images using Ziamath, including its bundled STIX math font.
Both inline and block formulas are supported; no browser or JavaScript is needed.

## Extending

Implement the abstract `Exporter[T]` base class to add new output formats:

```python
from jats_exporters.interface import Exporter

class MyExporter(Exporter[bytes]):
    def export(self, document) -> bytes: ...
```

## Requirements

- Python ≥ 3.13
- `lxml`, `xmlschema`, `jats-classes`
