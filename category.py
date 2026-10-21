
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://xnxx.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 14) "
        "AppleWebKit/537.36 Chrome/130.0.0.0 "
        "Mobile Safari/537.36"
    )
}


def scrape_page(session, url):
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def extract_video_data(data):
    videos = []

    if isinstance(data, dict):
        if data.get("@type") == "VideoObject":
            videos.append({
                "thumbnailUrl": data.get("thumbnailUrl"),
                "duration": data.get("duration"),
                "contentUrl": data.get("contentUrl"),
                "name": data.get("name")
            })

        for value in data.values():
            if isinstance(value, (dict, list)):
                videos.extend(extract_video_data(value))

    elif isinstance(data, list):
        for item in data:
            videos.extend(extract_video_data(item))

    return videos


def get_category(query):
    """
    Yields each video dictionary immediately after its page
    has been scraped. Extracts four fields only.
    """

    with requests.Session() as session:
        session.headers.update(HEADERS)

        start_url = urljoin(
            BASE_URL.rstrip("/") + "/",
            query.lstrip("/")
        )

        print(f"Opening: {start_url}", flush=True)

        try:
            soup = scrape_page(session, start_url)
        except requests.RequestException as error:
            print(f"Starting page error: {error}", flush=True)
            return

        links = []

        for element in soup.select(".thumb"):
            anchor = (
                element
                if element.name == "a" and element.get("href")
                else element.find("a", href=True)
            )

            if anchor and anchor.get("href"):
                links.append(urljoin(start_url, anchor["href"]))

        links = list(dict.fromkeys(links))
        print(f"Found {len(links)} video pages.", flush=True)

        for index, page_url in enumerate(links, start=1):
            print(
                f"[{index}/{len(links)}] Scraping: {page_url}",
                flush=True
            )

            try:
                page = scrape_page(session, page_url)

                for script in page.find_all(
                    "script",
                    attrs={"type": "application/ld+json"}
                ):
                    raw = script.string or script.get_text(strip=True)

                    if not raw:
                        continue

                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError:
                        continue

                    for video in extract_video_data(data):
                        # Deliver this video immediately
                        yield video

            except requests.RequestException as error:
                print(f"Page error: {error}", flush=True)



    

    
