
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://pornpics.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_soup(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_gallery():
    """
    Scrape the homepage.
    Returns each Wookmark tile's images and hrefs.
    """
    url = BASE_URL.rstrip("/") + "/"
    soup = get_soup(url)

    ul = soup.find("ul", class_="wookmark-initialised")

    if not ul:
        return []

    results = []

    for tile in ul.find_all("li"):
        images = [
            urljoin(url, img["data-src"])
            for img in tile.find_all(
                "img", attrs={"data-src": True}
            )
        ]

        hrefs = [
            urljoin(url, a["href"])
            for a in tile.find_all("a", href=True)
        ]

        results.append({
            "images": images,
            "hrefs": hrefs
        })

    return results


def get_profile(endpoint, root):
    """
    Scrape a search endpoint and its specified root path.

    endpoint: endpoint after the base URL.
    root: additional path relative to the endpoint.

    Returns mainEntity and image_data_srcs.
    """
    endpoint_url = urljoin(
        BASE_URL.rstrip("/") + "/",
        endpoint.lstrip("/")
    )

    url = urljoin(
        endpoint_url.rstrip("/") + "/",
        root.lstrip("/")
    )

    soup = get_soup(url)

    # Extract mainEntity from JSON-LD
    main_entities = []

    def find_main_entity(obj):
        if isinstance(obj, dict):
            if "mainEntity" in obj:
                main_entities.append(obj["mainEntity"])

            for value in obj.values():
                if isinstance(value, (dict, list)):
                    find_main_entity(value)

        elif isinstance(obj, list):
            for item in obj:
                find_main_entity(item)

    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):
        content = script.string or script.get_text(strip=True)

        try:
            data = json.loads(content)
            find_main_entity(data)
        except (json.JSONDecodeError, TypeError):
            continue

    # Extract image data-src values
    images = []
    ul = soup.find("ul", class_="wookmark-initialised")

    if ul:
        for img in ul.find_all(
            "img", attrs={"data-src": True}
        ):
            images.append(urljoin(url, img["data-src"]))

    return {
        "mainEntity": main_entities,
        "image_data_srcs": images
    }
