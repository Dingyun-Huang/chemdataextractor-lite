"""Small text helpers used by document readers and tokenizers."""

import codecs
import re


GREEK = set(
    "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
    "αβγδεζηθικλμνξοπρστυφχψω"
)


def get_encoding(input_string, guesses=None, is_html=False):
    """Return the declared or most likely encoding of a byte string."""
    if isinstance(input_string, str):
        return "utf-8"
    for bom, encoding in (
        (codecs.BOM_UTF8, "utf-8-sig"),
        (codecs.BOM_UTF32_LE, "utf-32-le"),
        (codecs.BOM_UTF32_BE, "utf-32-be"),
        (codecs.BOM_UTF16_LE, "utf-16-le"),
        (codecs.BOM_UTF16_BE, "utf-16-be"),
    ):
        if input_string.startswith(bom):
            return encoding
    head = input_string[:4096].decode("ascii", errors="ignore")
    declaration = re.search(
        r"(?:encoding\s*=\s*|charset\s*=\s*)[\"']?([A-Za-z0-9._-]+)",
        head,
        re.I,
    )
    if declaration:
        return declaration.group(1)
    candidates = ([guesses] if isinstance(guesses, str) else list(guesses or []))
    candidates.extend(("utf-8", "windows-1252"))
    for encoding in candidates:
        try:
            input_string.decode(encoding)
            return encoding
        except (LookupError, UnicodeDecodeError):
            continue
    return "utf-8"


def bracket_level(text, open=None, close=None):
    """Return zero when a string has balanced brackets or no brackets."""
    open = {"(", "[", "{"} if open is None else open
    close = {")", "]", "}"} if close is None else close
    level = 0
    for character in text:
        if character in open:
            level += 1
        elif character in close:
            level -= 1
    return level


__all__ = ["GREEK", "bracket_level", "get_encoding"]
