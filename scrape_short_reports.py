#!/usr/bin/env python3
"""
scrape_short_reports.py

Crawl a list of short-seller firm seed pages and extract report links (HTML posts and PDFs),
attempt to capture publication dates, short summaries, and optionally download PDFs.

Creates two datasets:
1. Detailed reports CSV with individual report information
2. Firms dataset CSV with summary statistics per short-selling firm

Usage:
    python scrape_short_reports.py --config firms.json --out-dir ./short_reports --download-pdfs

The firms.json config file should contain a list of firms with their websites, descriptions, and seed URLs.
See firms.json for an example configuration.
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from tqdm import tqdm

# ---------- Configurable defaults ----------
USER_AGENT = "Mozilla/5.0 (compatible; short-scraper/1.0; +https://example.com/bot)"
REQUEST_TIMEOUT = 20
DEFAULT_SLEEP = 2.0  # seconds between requests
RETRY_COUNT = 2
CSV_FIELDS = [
    "firm",
    "seed_url",
    "found_url",
    "title",
    "date_published",
    "snippet",
    "is_pdf",
    "local_path",
    "http_status",
    "fetched_at",
]

FIRMS_CSV_FIELDS = [
    "firm_name",
    "website",
    "description",
    "total_reports",
    "pdf_reports",
    "html_reports",
    "earliest_report_date",
    "latest_report_date",
    "seed_urls_scanned",
    "successful_fetches",
    "last_scanned_at",
]
# keywords to identify report links
REPORT_KEYWORDS = [
    "report",
    "research",
    "whitepaper",
    "pdf",
    "short",
    "analysis",
    "expose",
    "rebuttal",
    "investigation",
]


# ---------- Helper functions ----------
def safe_request(session, url, method="get", **kwargs):
    for attempt in range(RETRY_COUNT + 1):
        try:
            resp = session.request(method, url, timeout=REQUEST_TIMEOUT, **kwargs)
            return resp
        except requests.RequestException as e:
            if attempt >= RETRY_COUNT:
                raise
            sleep = 1.5 ** attempt
            logging.debug(f"Request failed for {url}: {e}. retrying in {sleep}s...")
            time.sleep(sleep)
    raise RuntimeError("unreachable")


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def clean_text(s: str):
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s).strip()
    return s


def find_date_from_meta(soup: BeautifulSoup):
    # common meta tags
    meta_props = [
        ('meta', {'property': 'article:published_time'}),
        ('meta', {'name': 'article:published_time'}),
        ('meta', {'property': 'og:published_time'}),
        ('meta', {'name': 'og:published_time'}),
        ('meta', {'name': 'pubdate'}),
        ('meta', {'name': 'publication_date'}),
        ('meta', {'name': 'date'}),
        ('time', {}),
    ]
    for tag, attrs in meta_props:
        for t in soup.find_all(tag, attrs=attrs):
            # try content or datetime or text
            val = t.get('content') or t.get('datetime') or t.get_text()
            val = clean_text(val)
            if val:
                try:
                    dt = dateparser.parse(val, fuzzy=True)
                    return dt.isoformat()
                except Exception:
                    continue
    # fallback: search for date-like strings in the page
    text = soup.get_text(" ", strip=True)
    m = re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[\w\.,\s\-]{0,40}\d{4})', text, re.IGNORECASE)
    if m:
        try:
            dt = dateparser.parse(m.group(1), fuzzy=True)
            return dt.isoformat()
        except Exception:
            return None
    return None


def extract_title(soup: BeautifulSoup):
    # try title tags
    if soup.title and soup.title.string:
        return clean_text(soup.title.string)
    # try common meta
    for meta in ('meta',):
        for name in ('og:title', 'twitter:title', 'title'):
            tag = soup.find('meta', attrs={'property': name}) or soup.find('meta', attrs={'name': name})
            if tag and tag.get('content'):
                return clean_text(tag['content'])
    # fallback: first h1
    h1 = soup.find('h1')
    if h1:
        return clean_text(h1.get_text())
    return None


def snippet_around_link(soup: BeautifulSoup, a_tag):
    # try paragraph parent or sibling
    p = a_tag.find_parent('p') or a_tag.find_parent(['article', 'div'])
    if p:
        return clean_text(p.get_text())
    # fallback: anchor text
    return clean_text(a_tag.get_text())


def is_pdf_link(href: str):
    return href.lower().split('?')[0].endswith('.pdf')


def looks_like_report(href: str, text: str):
    s = (href or "") + " " + (text or "")
    s = s.lower()
    for kw in REPORT_KEYWORDS:
        if kw in s:
            return True
    # also treat all pdfs as potential reports
    if is_pdf_link(href):
        return True
    return False


def normalize_url(base, href):
    if not href:
        return None
    href = href.strip()
    # ignore mailto:, javascript:, tel:
    if href.startswith("mailto:") or href.startswith("javascript:") or href.startswith("tel:"):
        return None
    return urljoin(base, href)


# ---------- Main scraping logic ----------
def process_seed(session, firm_name, seed_url, out_dir, download_pdfs=False, sleep_sec=DEFAULT_SLEEP):
    logging.info(f"[{firm_name}] scanning seed: {seed_url}")
    results = []
    try:
        resp = safe_request(session, seed_url, headers={"User-Agent": USER_AGENT})
    except Exception as e:
        logging.warning(f"Failed to fetch seed {seed_url}: {e}")
        return results

    if resp.status_code != 200:
        logging.warning(f"Seed {seed_url} returned status {resp.status_code}")
        return results

    page_html = resp.text
    soup = BeautifulSoup(page_html, "html.parser")
    anchors = soup.find_all('a', href=True)

    seen_urls = set()
    for a in anchors:
        raw_href = a.get('href')
        found = normalize_url(seed_url, raw_href)
        if not found:
            continue
        if found in seen_urls:
            continue
        seen_urls.add(found)

        link_text = clean_text(a.get_text())
        if not looks_like_report(found, link_text):
            # optionally also check if link points to a path that looks like '/reports/' or '/research/'
            parsed = urlparse(found)
            if re.search(r'/report[s]?/|/research/|/insights/|/investigation/|/whitepaper/|/publication/', parsed.path, flags=re.IGNORECASE):
                pass
            else:
                continue

        is_pdf = is_pdf_link(found)
        title = None
        date_published = None
        snippet = snippet_around_link(soup, a)
        local_path = ""
        http_status = None

        # If PDF: optionally download
        if is_pdf:
            try:
                logging.debug(f"Found PDF: {found}")
                head = safe_request(session, found, method="head", headers={"User-Agent": USER_AGENT})
                http_status = head.status_code
            except Exception:
                http_status = None

            if download_pdfs:
                # create dir
                pdf_dir = os.path.join(out_dir, "downloaded_pdfs", sanitize_filename(firm_name))
                ensure_dir(pdf_dir)
                try:
                    dl = safe_request(session, found, headers={"User-Agent": USER_AGENT}, stream=True)
                    http_status = dl.status_code
                    if dl.status_code == 200:
                        # filename guess
                        fname = guessed_filename_from_url(found) or f"report_{int(time.time())}.pdf"
                        local_file = os.path.join(pdf_dir, fname)
                        with open(local_file, "wb") as f:
                            for chunk in dl.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        local_path = local_file
                except Exception as e:
                    logging.warning(f"Could not download PDF {found}: {e}")

        else:
            # If HTML page, fetch it to try extract title/date
            try:
                link_resp = safe_request(session, found, headers={"User-Agent": USER_AGENT})
                http_status = link_resp.status_code
                if link_resp.status_code == 200 and 'text/html' in link_resp.headers.get('Content-Type', ''):
                    sub_soup = BeautifulSoup(link_resp.text, "html.parser")
                    title = extract_title(sub_soup) or link_text
                    date_published = find_date_from_meta(sub_soup)
                    if not snippet:
                        # use the first paragraph
                        p = sub_soup.find('p')
                        snippet = clean_text(p.get_text()) if p else ""
                else:
                    # fallback to link anchor text
                    title = link_text or found
            except Exception as e:
                logging.debug(f"Failed to fetch link page {found}: {e}")
                title = link_text or found

        results.append({
            "firm": firm_name,
            "seed_url": seed_url,
            "found_url": found,
            "title": title or "",
            "date_published": date_published or "",
            "snippet": snippet or "",
            "is_pdf": bool(is_pdf),
            "local_path": local_path,
            "http_status": http_status or "",
            "fetched_at": datetime.utcnow().isoformat()
        })

        time.sleep(sleep_sec)

    return results


def guessed_filename_from_url(url):
    p = urlparse(url).path
    name = os.path.basename(p)
    if name:
        return sanitize_filename(name)
    # if no basename, fallback
    return None


def sanitize_filename(s):
    return re.sub(r'[^A-Za-z0-9._-]', '_', s)


def save_as_csv(out_path, rows):
    ensure_dir(os.path.dirname(out_path) or ".")
    write_header = not os.path.exists(out_path)
    with open(out_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if write_header:
            writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in CSV_FIELDS})


def save_firms_csv(out_path, firm_summaries):
    ensure_dir(os.path.dirname(out_path) or ".")
    write_header = not os.path.exists(out_path)
    with open(out_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIRMS_CSV_FIELDS)
        if write_header:
            writer.writeheader()
        for firm_data in firm_summaries:
            writer.writerow({k: firm_data.get(k, "") for k in FIRMS_CSV_FIELDS})


# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(description="Scrape short-seller report links from seed pages.")
    parser.add_argument("--config", "-c", required=True, help="JSON config file listing firms and seed URLs.")
    parser.add_argument("--out-dir", "-o", default="./short_reports", help="Output directory for CSV and downloaded files.")
    parser.add_argument("--csv", default="reports.csv", help="CSV filename (inside out-dir) to append results.")
    parser.add_argument("--download-pdfs", action="store_true", help="Download discovered PDF reports.")
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP, help="Seconds to sleep between requests per link.")
    parser.add_argument("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING).")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO),
                        format="%(asctime)s [%(levelname)s] %(message)s")

    # load config
    if not os.path.exists(args.config):
        logging.error("Config file not found: %s", args.config)
        sys.exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    ensure_dir(args.out_dir)
    csv_path = os.path.join(args.out_dir, args.csv)
    firms_csv_path = os.path.join(args.out_dir, "firms_dataset.csv")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    all_rows = []
    firm_summaries = []
    firms = config.get("firms", [])

    for firm in firms:
        firm_name = firm.get("name")
        firm_website = firm.get("website", "")
        firm_description = firm.get("description", "")
        seed_urls = firm.get("seed_urls", [])

        if not seed_urls:
            logging.warning("No seed_urls for firm %s in config", firm_name)
            continue

        firm_rows = []
        successful_fetches = 0

        for seed in seed_urls:
            try:
                rows = process_seed(session, firm_name, seed, args.out_dir, download_pdfs=args.download_pdfs, sleep_sec=args.sleep)
                if rows:
                    firm_rows.extend(rows)
                    successful_fetches += 1
                    logging.info(f"Saved {len(rows)} results for {firm_name} from {seed}")
                else:
                    logging.info(f"No report-like links found for {firm_name} on {seed}")
            except Exception as e:
                logging.exception(f"Error processing seed {seed} for {firm_name}: {e}")

        # Calculate firm summary statistics
        if firm_rows:
            all_rows.extend(firm_rows)

            # Calculate statistics
            total_reports = len(firm_rows)
            pdf_reports = sum(1 for r in firm_rows if r.get("is_pdf"))
            html_reports = total_reports - pdf_reports

            # Find date range
            dates = []
            for r in firm_rows:
                date_str = r.get("date_published", "")
                if date_str:
                    try:
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        # Ensure all datetimes are timezone-aware
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        dates.append(dt)
                    except:
                        pass

            earliest_date = min(dates).isoformat() if dates else ""
            latest_date = max(dates).isoformat() if dates else ""

            firm_summary = {
                "firm_name": firm_name,
                "website": firm_website,
                "description": firm_description,
                "total_reports": total_reports,
                "pdf_reports": pdf_reports,
                "html_reports": html_reports,
                "earliest_report_date": earliest_date,
                "latest_report_date": latest_date,
                "seed_urls_scanned": len(seed_urls),
                "successful_fetches": successful_fetches,
                "last_scanned_at": datetime.utcnow().isoformat()
            }
            firm_summaries.append(firm_summary)

    # Save both CSVs
    if all_rows:
        save_as_csv(csv_path, all_rows)
        logging.info("Saved %d total report records to %s", len(all_rows), csv_path)

    if firm_summaries:
        save_firms_csv(firms_csv_path, firm_summaries)
        logging.info("Saved %d firm summaries to %s", len(firm_summaries), firms_csv_path)

    logging.info("Completed. Reports CSV: %s, Firms dataset: %s", csv_path, firms_csv_path)


if __name__ == "__main__":
    main()
