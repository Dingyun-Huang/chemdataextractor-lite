"""Document container and reader dispatch."""

import collections
import json
import logging
from pathlib import Path

from ..errors import ReaderError
from ..text import get_encoding
from .element import CaptionedElement
from .figure import Figure
from .meta import MetaData
from .table import Table
from .text import Caption, Cell, Citation, Footnote, Heading, Paragraph, Sentence, Title

log = logging.getLogger(__name__)


class Document(collections.abc.Sequence):
    """A format-neutral sequence of structural document elements."""

    def __init__(self, *elements):
        self._elements = []
        for element in elements:
            if isinstance(element, str):
                element = Paragraph(element)
            elif isinstance(element, bytes):
                encoding = get_encoding(element)
                log.warning("Guessed bytestring encoding as %s", encoding)
                element = Paragraph(element.decode(encoding))
            element.document = self
            self._elements.append(element)

    def __repr__(self):
        return f"<Document: {len(self)} elements>"

    __str__ = __repr__

    def __getitem__(self, index):
        return self.elements[index]

    def __len__(self):
        return len(self.elements)

    @property
    def elements(self):
        return self._elements

    @classmethod
    def from_file(cls, file, fname=None, readers=None):
        if isinstance(file, (str, bytes, Path)):
            path = Path(file)
            with path.open("rb") as stream:
                return cls.from_string(stream.read(), fname=fname or str(path), readers=readers)
        if fname is None and hasattr(file, "name"):
            fname = file.name
        return cls.from_string(file.read(), fname=fname, readers=readers)

    @classmethod
    def from_string(cls, content, fname=None, readers=None):
        if isinstance(content, str):
            content = content.encode("utf-8")
        if not isinstance(content, bytes):
            raise TypeError("content must be bytes or str")
        if readers is None:
            from ..reader import DEFAULT_READERS
            readers = DEFAULT_READERS
        errors = []
        for reader in readers:
            try:
                if not reader.detect(content, fname=fname):
                    continue
                document = reader.readstring(content)
                log.debug("Parsed document with %s", reader.__class__.__name__)
                return document
            except ReaderError as error:
                errors.append(error)
        message = "Unable to read document"
        if errors:
            message += f": {errors[-1]}"
        raise ReaderError(message)

    def get_element_with_id(self, id):
        pending = list(self.elements)
        while pending:
            element = pending.pop(0)
            if element.id == id:
                return element
            if element.elements:
                pending.extend(element.elements)
        return None

    def _elements_of_type(self, element_type):
        return [element for element in self.elements if isinstance(element, element_type)]

    @property
    def figures(self):
        return self._elements_of_type(Figure)

    @property
    def tables(self):
        return self._elements_of_type(Table)

    @property
    def citations(self):
        return self._elements_of_type(Citation)

    @property
    def footnotes(self):
        return self._elements_of_type(Footnote)

    @property
    def titles(self):
        return self._elements_of_type(Title)

    @property
    def headings(self):
        return self._elements_of_type(Heading)

    @property
    def paragraphs(self):
        return self._elements_of_type(Paragraph)

    @property
    def captions(self):
        return self._elements_of_type(Caption)

    @property
    def captioned_elements(self):
        return self._elements_of_type(CaptionedElement)

    @property
    def metadata(self):
        metadata = self._elements_of_type(MetaData)
        return metadata[0] if metadata else None

    @property
    def sentences(self):
        pending = list(self.elements)
        sentences = []
        while pending:
            element = pending.pop(0)
            if isinstance(element, Sentence) and not isinstance(element, Cell):
                sentences.append(element)
            elif element.elements:
                pending[0:0] = element.elements
        return sentences

    def heading_for_sentence(self, sentence):
        current_heading = None
        for element in self.elements:
            if isinstance(element, Heading):
                current_heading = element
                continue
            if sentence in (element.elements or []):
                return current_heading
        return None

    def serialize(self):
        return {"type": "document", "elements": [element.serialize() for element in self.elements]}

    def to_json(self, *args, **kwargs):
        return json.dumps(self.serialize(), *args, **kwargs)

    def _repr_html_(self):
        body = "\n".join(element._repr_html_() for element in self.elements if hasattr(element, "_repr_html_"))
        return f'<div class="cde-document">\n{body}\n</div>'
