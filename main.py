import requests
from bs4 import BeautifulSoup
import time

try:
    import lxml
except ImportError:
    print("`lxml` is not available, defaulting to `html.parser`")

url = "https://hardverapro.hu/aprok/notebook/apple/index.html"

try:
    response = requests.get(url)
    response.raise_for_status()

    html_content = response.text
    try:
        soup = BeautifulSoup(html_content, "lxml")
        print("Used `lxml` as a parser")
    except NameError:
        soup = BeautifulSoup(html_content, "html.parser")
        print("Used `html.parser` as a parser")

    prices = []
    price_elements = soup.find_all("div", class_="uad-price")
    names = []
    name_elements = soup.find_all("div", class_="uad-title")

    if price_elements:
        for price_element in price_elements:
            price = price_element.text.strip()
            prices.append(price)

        print(f"Found prices: {prices}")
    else:
        print("Price element not found on the page.")

    if name_elements:
        for name_element in name_elements:
            name = name_element.text.strip()
            names.append(name)

        print(f"Found names: {names}")
    else:
        print("Price element not found on the page.")

    time.sleep(1)

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
