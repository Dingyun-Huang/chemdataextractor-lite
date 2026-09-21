"""Bibliographic metadata document element."""

from .element import BaseElement


class MetaData(BaseElement):
    FIELDS = (
        "title", "authors", "publisher", "journal", "volume", "issue",
        "firstpage", "lastpage", "doi", "date", "language", "pdf_url", "html_url",
    )

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        normalized = {key.lstrip("_"): value for key, value in data.items()}
        self._data = {key: normalized.get(key) for key in self.FIELDS}

    def __repr__(self):
        return repr({key: value for key, value in self.data.items() if value})

    def __getattr__(self, name):
        if name in self.FIELDS:
            return self._data[name]
        raise AttributeError(name)

    @property
    def data(self):
        return dict(self._data)

    def serialize(self):
        return {"MetaData": {key: value for key, value in self._data.items() if value}}
