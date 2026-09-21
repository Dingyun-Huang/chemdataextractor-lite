"""Loader regressions ported from the original ChemDataExtractor tests.

The original suite also covered extraction, tagging, and model behavior.  This
module keeps the reader and document-loading cases that remain in ChemDataExtractor
Lite and adapts table assertions to the lite ``Table.table_data`` interface.
"""

from pathlib import Path

import pytest

from chemdataextractor import Document
from chemdataextractor.reader import (
    AcsHtmlReader,
    ElsevierXmlReader,
    HtmlReader,
    RscHtmlReader,
    SpringerHtmlReader,
    SpringerJatsReader,
    UsptoXmlReader,
)


DATA = Path(__file__).parent / "data"


def test_original_document_text_elements_and_iteration():
    elements = [
        "A first paragraph. With two sentences.",
        "A second paragraph.",
        "A third paragraph.",
    ]
    document = Document(*elements)

    assert document.elements[0].text == elements[0]
    assert document.elements[0].sentences[1].text == "With two sentences."
    assert document.elements[1].document is document
    assert len(document) == 3
    assert document[2].text == elements[2]
    assert [element.text for element in document] == elements


def test_original_document_decodes_bytestring_elements():
    document = Document(
        b"A first paragraph. With two sentences.",
        "A second paragraph. ©".encode("utf-8"),
        "A third paragraph (¶).".encode("windows-1252"),
    )

    assert document.elements[0].sentences[1].text == "With two sentences."
    assert document.elements[1].text == "A second paragraph. ©"
    assert document.elements[2].text == "A third paragraph (¶)."


def test_original_html_reader_paragraphs():
    document = HtmlReader().parse("<p>First para</p><p>Second Para</p>")

    assert len(document.elements) == 2
    assert [element.text for element in document.elements] == ["First para", "Second Para"]


def test_original_html_reader_recovers_unclosed_paragraphs():
    document = HtmlReader().parse("<p>First para<p>Second Para")

    assert len(document.elements) == 2
    assert [element.text for element in document.elements] == ["First para", "Second Para"]


@pytest.mark.parametrize(
    "markup",
    ["First line<br/>Second line", "<span>First line</span><br/><span>Second line</span>"],
)
def test_original_html_reader_linebreaks_split_paragraphs(markup):
    document = HtmlReader().parse(markup)

    assert len(document.elements) == 2
    assert [element.text for element in document.elements] == ["First line", "Second line"]


@pytest.mark.parametrize(
    ("reader_cls", "relative_path", "expected_count"),
    [
        (AcsHtmlReader, "acs/acs.jmedchem.6b00723.html", 198),
        (ElsevierXmlReader, "elsevier/j.jnoncrysol.2017.07.006.xml", 129),
        (RscHtmlReader, "rsc/10.1039_C6OB02074G.html", 59),
        (SpringerJatsReader, "springer/spr_test1.xml", 307),
        (UsptoXmlReader, "uspto/US06840965B2.xml", 112),
    ],
)
def test_original_readers_detect_and_load_directly(reader_cls, relative_path, expected_count):
    path = DATA / relative_path
    reader = reader_cls()
    content = path.read_bytes()

    assert reader.detect(content, fname=path.name)
    assert len(reader.readstring(content).elements) == expected_count


@pytest.mark.parametrize(
    ("reader_cls", "relative_path", "expected_count"),
    [
        (AcsHtmlReader, "acs/acs.jmedchem.6b00723.html", 198),
        (ElsevierXmlReader, "elsevier/j.jnoncrysol.2017.07.006.xml", 129),
        (RscHtmlReader, "rsc/10.1039_C6OB02074G.html", 59),
        (SpringerJatsReader, "springer/spr_test1.xml", 307),
        (UsptoXmlReader, "uspto/US06840965B2.xml", 112),
    ],
)
def test_original_readers_load_through_document(reader_cls, relative_path, expected_count):
    document = Document.from_file(DATA / relative_path, readers=[reader_cls()])

    assert len(document.elements) == expected_count


def test_original_elsevier_metadata():
    document = Document.from_file(
        DATA / "elsevier/j.jnoncrysol.2017.07.006.xml",
        readers=[ElsevierXmlReader()],
    )

    assert document.metadata.serialize() == {
        "MetaData": {
            "title": "STRUCTURALELECTROCHEMICALCHARACTERIZATIONCA50MG20CU25ZN5AMORPHOUSALLOY",
            "authors": ["BABILAS"],
            "publisher": "© 2017 Elsevier B.V. All rights reserved.",
            "journal": "Journal of Non-Crystalline Solids",
            "date": "2017-07-14",
            "volume": "471",
            "issue": "0022-3093",
            "firstpage": "467",
            "lastpage": "475",
            "doi": "10.1016/j.jnoncrysol.2017.07.006",
            "html_url": "https://sciencedirect.com/science/article/pii/S0022309317303496",
        }
    }


def test_original_rsc_metadata():
    document = Document.from_file(
        DATA / "rsc/10.1039_C6OB02074G.html",
        readers=[RscHtmlReader()],
    )

    assert document.metadata.serialize() == {
        "MetaData": {
            "title": "Denitrogenative hydrofluorination of aromatic aldehyde hydrazones using (difluoroiodo)toluene  ",
            "authors": [
                "Kaivalya G.\xa0Kulkarni",
                "Boris\xa0Miokovic",
                "Matthew\xa0Sauder",
                "Graham K.\xa0Murphy",
                "Kaivalya G.\xa0Kulkarni",
                "Boris\xa0Miokovic",
                "Matthew\xa0Sauder",
                "Graham K.\xa0Murphy",
            ],
            "publisher": "Royal Society of Chemistry",
            "journal": "Organic & Biomolecular Chemistry",
            "language": "en",
            "doi": "10.1039/C6OB02074G",
            "pdf_url": "http://pubs.rsc.org/en/Content/ArticlePDF/2016/OB/C6OB02074G",
            "html_url": "http://pubs.rsc.org/en/Content/ArticleLanding/2016/OB/C6OB02074G",
        }
    }


def test_original_elsevier_table_row_and_column_spans():
    document = Document.from_file(
        DATA / "elsevier/j.jnoncrysol.2018.02.024.xml",
        readers=[ElsevierXmlReader()],
    )

    assert [[cell.text for cell in row] for row in document.tables[0].table_data] == [
        [
            "Quantities",
            "Simulations data for melting/freezing temperature Tm",
            "Simulations data for melting/freezing temperature Tm",
            "Simulations data for melting/freezing temperature Tm",
        ],
        [
            "Quantities",
            "MD simulations with ReaxFF potential []",
            "MC simulations with ARK parameters []",
            "MD simulations with SW potential []",
        ],
        ["Tm (K)", "1500", "1750", "1775"],
        ["γC (K/s)", "2.36\u202f×\u202f1011", "4.25\u202f×\u202f1011", "4.95\u202f×\u202f1011"],
    ]


def test_original_springer_html_table_fixture():
    document = Document.from_file(DATA / "tables/table_test.html", readers=[SpringerHtmlReader()])

    assert len(document.elements) == 3
    assert len(document.tables) == 1
    table = document.tables[0]
    assert "Néel temperature" in table.caption.text
    assert [cell.text.strip() for cell in table.table_data[0]] == [
        "x",
        "TN (K)",
        "TD (K)",
        "μeff (obs.) (BM)",
        "μeff (cal.) (BM)",
        "Mn4+ spin",
        "Mn3+ spin",
    ]
