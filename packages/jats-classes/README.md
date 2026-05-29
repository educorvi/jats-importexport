# jats-classes

Domain models and parser for [JATS XML](https://jats.nlm.nih.gov/) documents.

## Overview

Provides Python classes that map to the core JATS article structure:

| Class | JATS element |
|---|---|
| `JATSDocument` | Root document wrapper |
| `Article` | `<article>` |
| `Front` | `<front>` (metadata) |
| `Body` | `<body>` |
| `Back` | `<back>` |
| `GenericSection` | Base class for `Section` and `Appendix` |
| `Section` | `<sec>` |
| `Appendix` | `<app>` |
| `AppendixGroup` | `<app-group>` |

## Usage

```python
from jats_classes import JATSDocument

doc = JATSDocument.from_xml(xml_string, xsd_path=None)
print(doc.article.front)
```

Optional XSD validation is performed when `xsd_path` is provided.

## Requirements

- Python ≥ 3.13
- `lxml`, `xmlschema`
