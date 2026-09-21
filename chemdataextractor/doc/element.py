"""Base classes for document elements."""

import json
from abc import ABCMeta, abstractmethod


class BaseElement(metaclass=ABCMeta):
    def __init__(self, document=None, references=None, id=None, **kwargs):
        self._document = document
        self.id = id
        self.references = list(references or [])

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    @property
    def document(self):
        return self._document

    @document.setter
    def document(self, document):
        self._document = document

    @property
    def elements(self):
        return None

    @abstractmethod
    def serialize(self):
        raise NotImplementedError

    def to_json(self, *args, **kwargs):
        return json.dumps(self.serialize(), *args, **kwargs)


class CaptionedElement(BaseElement):
    def __init__(self, caption, label=None, **kwargs):
        self.caption = caption
        self.label = label
        super().__init__(**kwargs)
        self.caption.document = self.document

    def __str__(self):
        return self.caption.text

    @BaseElement.document.setter
    def document(self, document):
        self._document = document
        self.caption.document = document

    @property
    def elements(self):
        return [self.caption]

    def serialize(self):
        data = {"type": self.__class__.__name__, "caption": self.caption.serialize()}
        if self.label is not None:
            data["label"] = self.label
        return data
