import io
from pathlib import Path
import subprocess
import sys

import pytest

from chemdataextractor import Document
from chemdataextractor.doc import Figure, Heading, Paragraph, Table, Title
from chemdataextractor.errors import ReaderError
from chemdataextractor.reader import (
    AcsHtmlReader,
    CsspHtmlReader,
    ElsevierXmlReader,
    HtmlReader,
    NlmXmlReader,
    PdfReader,
    PlainTextReader,
    RscHtmlReader,
    SpringerHtmlReader,
    SpringerJatsReader,
    UsptoXmlReader,
    XmlReader,
)


DATA = Path(__file__).parent / "data"


def test_manual_document_segments_sentences_and_tokens():
    document = Document("Costa et al. reported a value of 12 MPa. It was stable.")

    assert [sentence.text for sentence in document.sentences] == [
        "Costa et al. reported a value of 12 MPa.",
        "It was stable.",
    ]
    assert document.sentences[0].raw_tokens[-2:] == ["MPa", "."]
    assert document.sentences[0].tokens[0].start == 0


def test_from_string_accepts_text_and_bytes():
    text_document = Document.from_string("<p>alpha</p>", readers=[HtmlReader()])
    byte_document = Document.from_string(b"<p>beta</p>", readers=[HtmlReader()])

    assert text_document.paragraphs[0].text == "alpha"
    assert byte_document.paragraphs[0].text == "beta"


def test_from_file_accepts_paths_and_streams(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_bytes(b"First paragraph.\n\nSecond paragraph.")

    assert len(Document.from_file(path, readers=[PlainTextReader()])) == 2
    assert len(Document.from_file(io.BytesIO(path.read_bytes()), fname="sample.txt", readers=[PlainTextReader()])) == 2


def test_generic_html_preserves_structure_and_serializes_tables():
    html = b"""
    <html><head><meta name="citation_title" content="Example"></head><body>
      <h1>Title</h1><h2>Section</h2><p id="p1">Body text.</p>
      <figure><figcaption><span class="CaptionNumber">1</span>Figure caption</figcaption><img src="figure.png"></figure>
      <table><caption>Values</caption><thead><tr><th>Name</th><th>Value</th></tr></thead>
      <tbody><tr><td>A</td><td>12</td></tr></tbody></table>
    </body></html>
    """
    document = HtmlReader().readstring(html)

    assert isinstance(document.titles[0], Title)
    assert isinstance(document.headings[0], Heading)
    assert document.get_element_with_id("p1").text == "Body text."
    assert isinstance(document.figures[0], Figure)
    assert document.figures[0].links == ["figure.png"]
    assert isinstance(document.tables[0], Table)
    assert [[cell.text for cell in row] for row in document.tables[0].table_data] == [
        ["Name", "Value"], ["A", "12"]
    ]
    assert document.tables[0].raw_markup is None
    assert document.tables[0].serialize()["rows"] == [["Name", "Value"], ["A", "12"]]
    assert document.metadata.title == "Example"
    assert document.serialize()["type"] == "document"


@pytest.mark.parametrize(
    ("reader", "relative_path", "expected_count"),
    [
        (AcsHtmlReader(), "acs/acs.jmedchem.6b00723.html", 198),
        (RscHtmlReader(), "rsc/10.1039_C6OB02074G.html", 59),
        (ElsevierXmlReader(), "elsevier/j.jnoncrysol.2017.07.006.xml", 129),
        (UsptoXmlReader(), "uspto/US06840965B2.xml", 112),
        (SpringerJatsReader(), "springer/spr_test1.xml", 307),
    ],
)
def test_publisher_fixtures(reader, relative_path, expected_count):
    path = DATA / relative_path
    document = Document.from_file(path, readers=[reader])
    assert len(document) == expected_count


def test_default_reader_order_prefers_publisher_reader():
    document = Document.from_file(DATA / "elsevier/j.jnoncrysol.2017.07.006.xml")
    assert document.metadata.doi == "10.1016/j.jnoncrysol.2017.07.006"


def test_rsc_tables_keep_raw_html_markup():
    document = Document.from_file(DATA / "rsc/test_paper.html", readers=[RscHtmlReader()])

    assert len(document.tables) == 1
    table = document.tables[0]
    assert table.raw_markup.startswith('<div class="rtable__wrapper">')
    assert '<table class="tgroup rtable" border="0">' in table.raw_markup
    assert "Nanoporous NiO-capped" in table.raw_markup
    assert table.serialize()["raw_markup"] == table.raw_markup


def test_elsevier_tables_keep_raw_xml_markup():
    document = Document.from_file(
        DATA / "elsevier/j.jnoncrysol.2017.07.006.xml",
        readers=[ElsevierXmlReader()],
    )

    assert len(document.tables) == 2
    table = document.tables[0]
    assert table.raw_markup.startswith("<ce:table")
    assert '<ce:caption id="ca0070">' in table.raw_markup
    assert "<ce:italic>N</ce:italic>" in table.raw_markup
    assert '<tgroup cols="4">' in table.raw_markup
    assert table.serialize()["raw_markup"] == table.raw_markup


def test_nlm_reader_loads_jats():
    content = b'''<article xmlns="http://jats.nlm.nih.gov/ns/archiving/1.2/">
      <front><article-meta><title-group><article-title>Example</article-title></title-group></article-meta></front>
      <body><sec><title>Results</title><p>A result.</p></sec></body>
    </article>'''
    document = Document.from_string(content, fname="example.nxml", readers=[NlmXmlReader()])
    assert document.titles[0].text == "Example"
    assert document.headings[0].text == "Results"


def test_cssp_and_springer_html_readers_load_markup():
    cssp = b'''<html><head><meta name="DC.Publisher" content="ChemSpider SyntheticPages"></head>
      <body><div class="article-container"><h2>CSSP title</h2><p>Text.</p></div></body></html>'''
    springer = b'''<html><head><meta content="SpringerLink"></head><body>
      <h1 class="ArticleTitle">Springer title</h1><p>Text.</p></body></html>'''

    assert Document.from_string(cssp, fname="paper.html", readers=[CsspHtmlReader()]).titles[0].text == "CSSP title"
    assert Document.from_string(springer, fname="paper.html", readers=[SpringerHtmlReader()]).titles[0].text == "Springer title"


def test_generic_xml_and_reader_errors():
    document = Document.from_string(b"<article><p>Text.</p></article>", fname="paper.xml", readers=[XmlReader()])
    assert document.paragraphs[0].text == "Text."
    with pytest.raises(ReaderError):
        Document.from_string(b"not a pdf", fname="paper.pdf", readers=[PdfReader()])


def _minimal_pdf(text):
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode("ascii") + body + b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return bytes(output)


def test_pdf_reader_extracts_paragraphs():
    document = Document.from_string(_minimal_pdf("Hello PDF."), fname="paper.pdf", readers=[PdfReader()])
    assert any("Hello PDF." in paragraph.text for paragraph in document.paragraphs)


def test_extraction_api_is_absent():
    document = Document("Text.")
    paragraph = document.paragraphs[0]
    assert not hasattr(document, "records")
    assert not hasattr(document, "models")
    assert not hasattr(paragraph, "records")
    assert not hasattr(document.sentences[0].tokens[0], "pos_tag")


def test_import_does_not_load_removed_heavy_dependencies():
    command = [
        sys.executable,
        "-c",
        "import sys, chemdataextractor; "
        "blocked=('transformers','stanza','scipy','sklearn','torch','selenium','boto3'); "
        "assert not any(name in sys.modules for name in blocked)",
    ]
    subprocess.run(command, check=True)
