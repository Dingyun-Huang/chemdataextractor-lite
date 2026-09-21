# ChemDataExtractor Lite

ChemDataExtractor Lite converts scientific HTML, XML, PDF, and plain-text files into a consistent `Document` object. It keeps document structure, metadata, tables, figures, references, sentence segmentation, and chemistry-aware word segmentation without the tagging and extraction stack from ChemDataExtractor 2.

## Installation

```bash
pip install -e .
```

The chemistry-trained sentence model is included in the package, so document loading and segmentation work offline after installation.

## Usage

```python
from chemdataextractor import Document

document = Document.from_file("article.xml")

for element in document:
    if hasattr(element, "text"):
        print(type(element).__name__, element.text)

for sentence in document.sentences:
    print(sentence.text)
    print(sentence.raw_tokens)
```

`Document.from_string` accepts `bytes` or Unicode text. Both loading methods accept an optional `readers` list when explicit format handling is needed.

## Supported readers

- Generic HTML and XML
- ACS, RSC, CSSP, and Springer HTML
- Elsevier, NLM/JATS, Springer JATS, and USPTO XML
- PDF through `pdfminer.six`
- Plain text

Publisher-specific readers run before generic fallbacks. Readers preserve titles, headings, paragraphs, citations, footnotes, metadata, figure captions and links, table captions, and raw table cells when the source exposes them.

RSC HTML and Elsevier XML tables also retain their pre-cleaning markup fragment as `Table.raw_markup`. The value is included as `raw_markup` when the table or document is serialized. Tables loaded by other readers currently set this attribute to `None`.

## Document model

The public import namespace remains `chemdataextractor`. Structural classes are available from `chemdataextractor.doc`, and readers from `chemdataextractor.reader`.

Extraction APIs from ChemDataExtractor 2 are intentionally absent: models, parsers, records, POS/NER tagging, chemical mention detection, relation extraction, scraping clients, and model downloads are outside this package.

## Development

```bash
python -m pip install -e .
python -m pip install pytest build
python -m pytest
python -m build
```

The project is released under the MIT license. The bundled `punkt_chem-1.0.pickle` sentence model is the chemistry Punkt model distributed by the ChemDataExtractor project.
