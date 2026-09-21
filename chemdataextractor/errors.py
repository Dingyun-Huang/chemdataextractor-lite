"""Public exceptions raised by document loaders."""


class ChemDataExtractorError(Exception):
    """Base package exception."""


class ReaderError(ChemDataExtractorError):
    """Raised when a reader cannot load a document."""
