from pathlib import Path

import pytest

from scraper import parse_book, parse_listing, parse_price, save

FIXTURES = Path(__file__).parent / "fixtures"
PAGE_URL = "https://books.toscrape.com/catalogue/page-2.html"


def load(name):
    return (FIXTURES / name).read_bytes()


def test_listing_page():
    books, next_url = parse_listing(load("listing.html"), PAGE_URL)

    assert len(books) == 20
    assert books[0] == {
        "title": "In Her Wake",
        "price": 12.84,
        "rating": 1,
        "in_stock": True,
        "url": "https://books.toscrape.com/catalogue/in-her-wake_980/index.html",
    }
    assert next_url == "https://books.toscrape.com/catalogue/page-3.html"


def test_last_page_has_no_next():
    books, next_url = parse_listing(load("last_page.html"), PAGE_URL.replace("2", "50"))
    assert books
    assert next_url is None


def test_book_page():
    book = parse_book(load("book.html"))

    assert book["upc"] == "a897fe39b1053632"
    assert book["category"] == "Poetry"
    assert book["stock_count"] == 22
    assert book["reviews"] == 0
    assert book["description"].startswith("It's hard to imagine a world without")
    assert not book["description"].endswith("more")


@pytest.mark.parametrize("text,expected", [("£51.77", 51.77), ("Â£9.00", 9.0), ("", None)])
def test_parse_price(text, expected):
    assert parse_price(text) == expected


def test_scraped_formulas_stay_text(tmp_path):
    from openpyxl import load_workbook

    books = [{"title": "=HYPERLINK(\"http://evil.example\")", "price": -1.0}]
    save(books, tmp_path / "b.xlsx")
    cell = load_workbook(tmp_path / "b.xlsx").active["A2"]
    assert cell.data_type == "s"

    save(books, tmp_path / "b.csv")
    text = (tmp_path / "b.csv").read_text(encoding="utf-8-sig")
    assert "'=HYPERLINK" in text
    assert ",-1.0" in text


@pytest.mark.parametrize("ext", ["csv", "json", "xlsx"])
def test_save_formats(tmp_path, ext):
    books, _ = parse_listing(load("listing.html"), PAGE_URL)
    out = tmp_path / f"books.{ext}"
    save(books, out)
    assert out.stat().st_size > 0
