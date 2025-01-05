import requests
from bs4 import BeautifulSoup
import time
import lxml
import pandas as pd
import numpy
import openpyxl

URL = "https://hardverapro.hu/aprok/notebook/apple/index.html"

response = requests.get(URL)
response.raise_for_status()

html_content = response.text
soup = BeautifulSoup(html_content, "lxml")

prices = []
listings = []

price_elements = soup.find_all("div", class_="uad-price")
listing_elements = soup.find_all("div", class_="uad-title")

for price_element in price_elements:
    price = price_element.text.strip()
    prices.append(price)

for listing_element in listing_elements:
    listing = listing_element.text.strip()
    listings.append(listing)


prices_series = pd.Series(prices)
listings_series = pd.Series(listings)

df = pd.DataFrame(prices, index=listings_series, columns=["price"]) # underlines, despite it working
print(df)

# df.to_csv("test.csv", sep=";")
df.to_excel("test.xlsx")
