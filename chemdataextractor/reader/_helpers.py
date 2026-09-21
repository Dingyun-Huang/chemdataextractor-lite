"""Small tree transforms shared by publisher readers."""

import re


def replace_rsc_img_chars(document):
    image_re = re.compile(
        r"https?://www\.rsc\.org/images/entities/(?:h[23]+_)?(?:[ib]+_)?char_"
        r"([0-9a-f]{4})(?:_([0-9a-f]{4}))?\.gif"
    )
    for img in document.xpath('.//img[contains(@src, "rsc.org/images/entities/")]'):
        match = image_re.match(img.get("src", ""))
        if not match:
            continue
        replacement = "".join(chr(int(code, 16)) for code in match.groups() if code)
        replacement += img.tail or ""
        parent = img.getparent()
        if parent is None:
            continue
        previous = img.getprevious()
        if previous is None:
            parent.text = (parent.text or "") + replacement
        else:
            previous.tail = (previous.tail or "") + replacement
        parent.remove(img)
    return document


def space_labels(document):
    for label in document.xpath(".//bold"):
        if not label.text or not re.match(r"^\(L?\d\d?[a-z]?\):?$", label.text, re.I):
            continue
        previous = label.getprevious()
        if previous is None:
            label.getparent().text = (label.getparent().text or "").rstrip() + " "
        else:
            previous.tail = (previous.tail or "").rstrip() + " "
        label.tail = " " + (label.tail or "").lstrip()
    return document


def _tidy_references(document, xpath, tag):
    for reference in document.xpath(xpath):
        parent = reference.getparent()
        previous = reference.getprevious()
        before = (parent.text if previous is None else previous.tail) or ""
        stripped = before.rstrip()
        if stripped.endswith(("[", "(")):
            before = stripped[:-1]
        if previous is None:
            parent.text = before
        else:
            previous.tail = before
        following = reference.getnext()
        if following is not None and following.tag == tag and (reference.tail or "").strip() in {",", "-", "–", "−"}:
            reference.tail = ""
        tail = (reference.tail or "").lstrip()
        reference.tail = tail[1:] if tail.startswith(("]", ")")) else tail
    return document


def tidy_nlm_references(document):
    return _tidy_references(document, './/xref[@ref-type="bibr"]', "xref")


def tidy_springer_references(document):
    return _tidy_references(document, ".//abbrgrp", "abbrgrp")
