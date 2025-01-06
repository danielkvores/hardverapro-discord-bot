import requests # to get URL
from bs4 import BeautifulSoup # to scrape the website
import time # unused, will be used to make it wait
import lxml # for bs4
import pandas as pd
import numpy # unused, might use later
import openpyxl # used for exporting to excel


def rich_display_dataframe(df, title):
    """Function do display the data nicely for CLI. Not needed for excel, etc."""
    import contextlib
    from rich import print
    from rich.table import Table
    from rich.errors import NotRenderableError

    df = df.astype(str)
    table = Table(title=title)
    for col in df.columns:
        table.add_column(col)
    for row in df.values:
        with contextlib.suppress(NotRenderableError):
            table.add_row(*row)
    print(table)


URL = "https://hardverapro.hu/aprok/notebook/apple/index.html"

response = requests.get(URL)
response.raise_for_status()

html_content = response.text
soup = BeautifulSoup(html_content, "lxml")


price_elements = soup.find_all("div", class_="uad-price")
listing_elements = soup.find_all("div", class_="uad-title")
review_elements = soup.find_all("span", class_="uad-rating")
other_elements = soup.find_all("div", class_="uad-light")
location_and_username = [other_element.text.strip() for other_element in other_elements]


data = {
    "Listing name": [
        listing_element.text.strip() for listing_element in listing_elements
    ],
    "Price": [price_element.text.strip() for price_element in price_elements],
    "Reviews": [review_element.text.strip() for review_element in review_elements],
    "Username": [
        location_and_username[i] for i in range(1, len(location_and_username), 3)
    ],
    "Location": [
        location_and_username[i] for i in range(0, len(location_and_username), 3)
    ],
}

df = pd.DataFrame(data)

rich_display_dataframe(df, title="Hardverapro")
