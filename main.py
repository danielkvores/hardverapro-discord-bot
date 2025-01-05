import requests
import time
from bs4 import BeautifulSoup
import lxml


def fetch_html(url):
    """Fetches the HTML content from a URL, handles request errors."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def parse_html(html_content):
    """Parses the HTML content with lxml if available, falls back to html.parser."""
    if not html_content:
        return None
    try:
        soup = BeautifulSoup(html_content, "lxml")
        print("Used 'lxml' as parser")
        return soup
    except NameError:
        soup = BeautifulSoup(html_content, "html.parser")
        print("Used 'html.parser' as parser")
        return soup


def extract_data(soup, element_type, class_name):
    """Extract data using specified type and class"""
    data = []
    elements = soup.find_all(element_type, class_=class_name)
    if elements:
        for element in elements:
            data.append(element.text.strip())

        return data
    else:
        print(f"{element_type} elements with class name {class_name} not found")
        return None


def process_url(url):
    """Fetches, parses, and extract data from given URL."""
    html_content = fetch_html(url)
    if not html_content:
        return

    soup = parse_html(html_content)
    if not soup:
        return
    prices = extract_data(soup, "div", "uad-price")
    if prices:
        print(f"Found prices: {prices}")

    names = extract_data(soup, "div", "uad-title")
    if names:
        print(f"Found names: {names}")
    time.sleep(1)


if __name__ == "__main__":
    urls = ["https://hardverapro.hu/aprok/notebook/apple/index.html"]
    for url in urls:
        process_url(url)
