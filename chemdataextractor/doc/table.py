"""Structural table document element."""

from .element import CaptionedElement
from .text import Cell


class Table(CaptionedElement):
    def __init__(self, caption, label=None, table_data=None, footnotes=None, raw_markup=None, **kwargs):
        super().__init__(caption=caption, label=label, **kwargs)
        self.table_data = [
            [cell if isinstance(cell, Cell) else Cell(str(cell)) for cell in row]
            for row in (table_data or [])
        ]
        self.footnotes = list(footnotes or [])
        self.raw_markup = raw_markup
        self.document = self.document

    @CaptionedElement.document.setter
    def document(self, document):
        self._document = document
        self.caption.document = document
        for row in getattr(self, "table_data", []):
            for cell in row:
                cell.document = document
        for footnote in getattr(self, "footnotes", []):
            footnote.document = document

    @property
    def elements(self):
        return [cell for row in self.table_data for cell in row] + [self.caption] + self.footnotes

    def serialize(self):
        data = super().serialize()
        data["rows"] = [[cell.text for cell in row] for row in self.table_data]
        if self.footnotes:
            data["footnotes"] = [footnote.serialize() for footnote in self.footnotes]
        if self.raw_markup is not None:
            data["raw_markup"] = self.raw_markup
        return data
