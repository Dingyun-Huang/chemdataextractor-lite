"""Text document elements with sentence and word segmentation."""

import collections
import unicodedata

from ..nlp.tokenize import ChemSentenceTokenizer, ChemWordTokenizer
from .element import BaseElement


class Span:
    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end

    def __repr__(self):
        return f"{self.__class__.__name__}({self.text!r}, {self.start!r}, {self.end!r})"

    def __str__(self):
        return self.text

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.text == other.text
            and self.start == other.start
            and self.end == other.end
        )

    def __hash__(self):
        return hash((self.text, self.start, self.end))

    @property
    def length(self):
        return self.end - self.start


class Token(Span):
    pass


# Kept as an import alias for loader clients that used the old token class name.
RichToken = Token


class BaseText(BaseElement):
    def __init__(self, text, **kwargs):
        if not isinstance(text, str):
            raise TypeError("Text must be a unicode string")
        super().__init__(**kwargs)
        self._text = text

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(id={self.id!r}, "
            f"references={self.references!r}, text={self.text!r})"
        )

    def __str__(self):
        return self.text

    @property
    def text(self):
        return self._text

    def serialize(self):
        data = {"type": self.__class__.__name__, "content": self.text}
        if self.id is not None:
            data["id"] = self.id
        if self.references:
            data["references"] = self.references
        return data

    def _repr_html_(self):
        return self.text


class Text(collections.abc.Sequence, BaseText):
    sentence_tokenizer = ChemSentenceTokenizer()
    word_tokenizer = ChemWordTokenizer()

    def __init__(self, text, sentence_tokenizer=None, word_tokenizer=None, **kwargs):
        super().__init__(text, **kwargs)
        self.sentence_tokenizer = sentence_tokenizer or self.sentence_tokenizer
        self.word_tokenizer = word_tokenizer or self.word_tokenizer
        self._sentences = None

    def __getitem__(self, index):
        return self.sentences[index]

    def __len__(self):
        return len(self.sentences)

    @property
    def sentences(self):
        if self._sentences is None:
            spans = self.sentence_tokenizer.span_tokenize(self.text)
            self._sentences = [
                Sentence(
                    self.text[start:end],
                    start=start,
                    end=end,
                    word_tokenizer=self.word_tokenizer,
                    document=self.document,
                )
                for start, end in spans
            ]
        return self._sentences

    @BaseElement.document.setter
    def document(self, document):
        self._document = document
        if self._sentences is not None:
            for sentence in self._sentences:
                sentence.document = document

    @property
    def elements(self):
        return self.sentences

    @property
    def raw_sentences(self):
        return [sentence.text for sentence in self.sentences]

    @property
    def tokens(self):
        return [sentence.tokens for sentence in self.sentences]

    @property
    def raw_tokens(self):
        return [sentence.raw_tokens for sentence in self.sentences]

    def __add__(self, other):
        if type(self) is type(other):
            return self.__class__(
                self.text + other.text,
                id=self.id or other.id,
                references=self.references + other.references,
                sentence_tokenizer=self.sentence_tokenizer,
                word_tokenizer=self.word_tokenizer,
            )
        return NotImplemented


class Title(Text):
    def _repr_html_(self):
        return f'<h1 class="cde-title">{self.text}</h1>'


class Heading(Text):
    def _repr_html_(self):
        return f'<h2 class="cde-heading">{self.text}</h2>'


class Paragraph(Text):
    def _repr_html_(self):
        return f'<p class="cde-paragraph">{self.text}</p>'


class Footnote(Text):
    pass


class Citation(Text):
    pass


class Caption(Text):
    pass


class Sentence(collections.abc.Sequence, BaseText):
    word_tokenizer = ChemWordTokenizer()

    def __init__(self, text, start=0, end=None, word_tokenizer=None, **kwargs):
        super().__init__(text, **kwargs)
        self.start = start
        self.end = len(text) if end is None else end
        self.word_tokenizer = word_tokenizer or self.word_tokenizer
        self._tokens = None

    def __getitem__(self, index):
        return self.tokens[index]

    def __len__(self):
        return len(self.tokens)

    @property
    def tokens(self):
        if self._tokens is None:
            spans = self.word_tokenizer.span_tokenize(self.text)
            self._tokens = [
                Token(
                    "".join(ch for ch in self.text[left:right] if unicodedata.category(ch)[0] != "C"),
                    left + self.start,
                    right + self.start,
                )
                for left, right in spans
            ]
        return self._tokens

    @property
    def raw_tokens(self):
        return [token.text for token in self.tokens]

    @property
    def elements(self):
        return None

    def __add__(self, other):
        if type(self) is type(other):
            return self.__class__(
                self.text + other.text,
                start=self.start,
                end=self.start + len(self.text + other.text),
                id=self.id or other.id,
                references=self.references + other.references,
                word_tokenizer=self.word_tokenizer,
            )
        return NotImplemented


class Cell(Sentence):
    pass
