"""Internal markup utilities retained for document readers."""

BLOCK_ELEMENTS = {
    "p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "pre", "dd", "dl", "div",
    "noscript", "blockquote", "form", "hr", "table", "fieldset", "address", "article", "aside",
    "audio", "canvas", "figcaption", "figure", "footer", "header", "hgroup", "output", "section",
    "body", "head", "title", "tr", "td", "th", "thead", "tfoot", "dt", "li", "tbody",
}

INLINE_ELEMENTS = {
    "b", "big", "i", "small", "tt", "abbr", "acronym", "cite", "code", "dfn", "em", "kbd",
    "strong", "samp", "var", "a", "bdo", "br", "img", "map", "object", "q", "script", "span",
    "sub", "sup", "button", "input", "label", "select", "textarea", "blink", "font", "marquee",
    "nobr", "s", "strike", "u", "wbr",
}
