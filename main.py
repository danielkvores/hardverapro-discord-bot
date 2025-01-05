import requests
from bs4 import BeautifulSoup
import time
import lxml
import pandas as pd
import numpy
import openpyxl

def rich_display_dataframe(df, title):
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
other_elements = soup.find_all("span", class_="uad-rating")


data = {
    "Listing name": [listing_element.text.strip() for listing_element in listing_elements],
    "Price": [price_element.text.strip() for price_element in price_elements],
    "Reviews": [other_element.text.strip() for other_element in other_elements]
}

df = pd.DataFrame(data)

rich_display_dataframe(df, title="Hardverapro")

"""
idea: make this run constantly and update every 15 minutes f.e.
and make the new listings appear in a different colour thanks to rich

idea2: add cli arguments with which you can specify price ranges, etc.

idea3: maybe it could also check whether you have new notifications,
and make that the text in the title of the dataframe, like
"x unread messages"
"""
