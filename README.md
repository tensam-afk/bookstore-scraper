# bookstore-scraper

![tests](https://github.com/tensam-afk/bookstore-scraper/actions/workflows/tests.yml/badge.svg)

Crawls the full catalogue of [books.toscrape.com](https://books.toscrape.com) (1,000 books over 50 pages) and exports it to CSV, JSON or Excel.

**The typical client request:** "I need every product from this site in a spreadsheet: name, price, rating, stock, category. And I'll need it again next month."

**What you get:** one command that produces the spreadsheet, filtered however you need, which you can re-run any time. Nobody has to copy and paste anything.

| | |
|---|---|
| Listing pages only, whole catalogue | ~40 seconds, 1,000 rows |
| With detail pages (8 parallel workers) | 60 books in ~9 seconds |
| Output | `.xlsx` (frozen header, filters on), `.csv` (opens cleanly in Excel), `.json` |
| Failures | 429 and 5xx responses retried with backoff; one bad page doesn't stop the run |

I use it as a template for client scraping jobs. The site changes, but the parts stay the same: pagination, detail pages, retries, rate limiting and clean exports.

## What it does

- Follows the "next" link until it runs out of pages (or stops after `--pages N`)
- Pulls title, price, star rating, stock status and URL from each listing
- With `--details`, it also visits every book page (in parallel) and adds UPC, category, exact stock count, review count and description
- Retries on 429 and 5xx responses with backoff, and waits briefly between requests
- Filters by rating or price before saving
- CSV is written with a BOM so Excel opens it without mangling characters. The `.xlsx` export has a frozen header row and filters turned on.

## Setup

```
pip install -r requirements.txt
```

## Usage

```
# whole catalogue, listing data only (~40s)
python scraper.py -o output/books.csv

# first 3 pages with full details, to Excel
python scraper.py --pages 3 --details -o output/books.xlsx

# 4+ star books under £20, as JSON
python scraper.py --min-rating 4 --max-price 20 -o output/cheap_good_books.json

# a single category
python scraper.py --url https://books.toscrape.com/catalogue/category/books/mystery_3/index.html -d
```

Run `python scraper.py -h` for all options.

## Sample output

The first rows of `python scraper.py --pages 1 --details -o books.xlsx` (some columns left out here; the file also has `in_stock`, `url`, `reviews` and `description`):

| title | price | rating | category | stock_count | upc |
|---|---|---|---|---|---|
| A Light in the Attic | 51.77 | 3 | Poetry | 22 | a897fe39b1053632 |
| Tipping the Velvet | 53.74 | 1 | Historical Fiction | 20 | 90fa61229261140a |
| Soumission | 50.1 | 1 | Fiction | 20 | 6957f44c3847a760 |
| Sharp Objects | 47.82 | 4 | Mystery | 20 | e00eb4fd7b871a48 |
| Sapiens: A Brief History of Humankind | 54.23 | 5 | History | 20 | 4165285e1663650f |

## Tests

The parsing tests run against saved copies of real pages in `tests/fixtures`, so they don't touch the network.

```
python -m pytest
```

## Adapting it to another site

Most of the work is in `parse_listing` and `parse_book`. Swap the CSS selectors, keep the crawl loop, and check the target site's robots.txt and terms first. If the site renders its content with JavaScript, use Playwright instead of `requests`.

Text that starts with `=`, `+`, `-` or `@` is written as plain text, not a formula, so a hostile page can't plant a working formula in the spreadsheet.

## License

MIT
