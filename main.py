import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import json

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

URL = "https://hardverapro.hu/aprok/mobil/mobil/iphone/iphone_14_2/iphone_14_pro/index.html"

response = requests.get(URL)
response.raise_for_status()

html_content = response.text
soup = BeautifulSoup(html_content, "lxml")

price_elements = soup.find_all("div", class_="uad-price")
listing_elements = soup.find_all("div", class_="uad-title")
review_elements = soup.find_all("span", class_="uad-rating")
other_elements = soup.find_all("div", class_="uad-light")
location_and_username = [other_element.text.strip() for other_element in other_elements]
link_elements = [listing_element.find('a')['href'] for listing_element in listing_elements]

# Process only the first listing
if listing_elements:
    data = {
        "Listing name": listing_elements[0].text.strip(),
        "Price": price_elements[0].text.strip(),
        "Reviews": review_elements[0].text.strip(),
        "Username": location_and_username[1],
        "Location": location_and_username[0],
        "Link": link_elements[0],
        "Description": "",
        "Status": "",
        "Condition": "",
        "Avatar": "",
        "Images": []
    }

    time.sleep(1.05)  # To avoid hitting rate limits
    response = requests.get(data["Link"])
    response.raise_for_status()

    html_content = response.text
    soup = BeautifulSoup(html_content, "lxml")

    description_elements = soup.find_all("div", class_="uad-content")
    for description_element in description_elements:
        for br in description_element.find_all("br"):
            br.replace_with("\n")
        data["Description"] = description_element.text.replace("Tetszik", "").strip()[:1023]
        if len(data["Description"]) > 1000:
            data["Description"] = data["Description"][:1000] + "..."
    status_elements = soup.find_all("th", string="Állapot:")
    condition_elements = soup.find_all("th", string="Állapot:")
    avatar_elements = soup.find_all("div", class_="carousel-item active")
    image_elements = soup.find_all("div", class_="carousel-item")

    status_element = soup.find("th", string="Állapot:")
    if status_element:
        data["Status"] = status_element.find_next_sibling("td").text.strip()

    condition_element = soup.find("th", string="Szándék:")
    if condition_element:
        data["Condition"] = condition_element.find_next_sibling("td").text.strip()

    for avatar_element in avatar_elements:
        data["Avatar"] = "https:" + avatar_element.find("img")["src"]

    for image_element in image_elements:
        image_source = image_element.find("a")["href"]
        if image_source:
            data["Images"].append("https:" + image_source)
        if len(data["Images"]) == 4:
            break

    Webhook_URL = "YOUR DISCORD WEBHOOK"

embed_data = {
    "content": None,
    "embeds": [
        {
            "title": data["Listing name"],
            "url": data["Link"],
            "color": 16750848,
            "fields": [
                {
                    "name": "> __Ár: __",
                    "value": f"`{data['Price']}`"
                },
                {
                    "name": "> __Lokáció:__",
                    "value": f"`{data['Location']}`"
                },
                {
                    "name": "> __Hirdető:__",
                    "value": f"`{data['Username']}`"
                },
                {
                    "name": "> __Hírdető értékelései:__",
                    "value": f"`{data['Reviews']}`"
                },
                {
                    "name": "> __Leírás:__",
                    "value": f"`{data['Description']}`"
                },
                {
                    "name": "> __Állapot:__",
                    "value": f"`{data['Status']}`"
                },
                {
                    "name": "> __Szándék:__",
                    "value": f"`{data['Condition']}`"
                }
            ],
            "author": {
                "name": "Új listing jelent meg az oldalon!",
                "url": data["Link"],
                "icon_url": data["Avatar"]
            },
            "footer": {
                "text": "@KvoDani, @DinnyOS"
            },
            "image": {
                "url": data["Avatar"]
            },
        },
    ],
    "attachments": []
}

# Adding more images if available to a different embed
for i in range(1, min(4, len(data["Images"]))):  # Maximum 4 pictures
    embed_data["embeds"].append({
        "color": 16750848,
        "title": f"__{i+1}. kép:__",
        "image": {
            "url": data["Images"][i]
        },
        "footer": {
            "text": "@DinnyOS, @KvoDani"
        },
    })


# Convert embed_data to JSON string
embed_data_json = json.dumps(embed_data)


# Print the embed data for debugging
print("Embed Data:", embed_data)

response = requests.post(Webhook_URL, json=embed_data)
response.raise_for_status()
time.sleep(0.65)  # To avoid hitting rate limits
