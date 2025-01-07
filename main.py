import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import json
import os

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

def save_to_excel(data, filename="listings.xlsx"):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

def load_from_excel(filename="listings.xlsx"):
    if os.path.exists(filename):
        return pd.read_excel(filename).to_dict(orient='records')
    return []

def get_listing_data(soup):
    price_elements = soup.find_all("div", class_="uad-price")
    listing_elements = soup.find_all("div", class_="uad-title")
    
    location_elements = []
    for element in soup.find_all("div", class_="uad-info"):
        span_element = element.find("span")
        if span_element and "data-original-title" in span_element.attrs:
            location_elements.append(span_element["data-original-title"])
        else:
            location_elements.append(element.find("div", class_="uad-light").text.strip())

    rating_elements = []
    for element in soup.find_all("div", class_="uad-misc"):
        rating_span = element.find("span", class_="uad-rating")
        if rating_span and "data-original-title" in rating_span.attrs:
            #  If "data-original-title" is present, we use that as the rating
            rating_text = rating_span["data-original-title"].strip()
            rating_elements.append(rating_text)
        elif rating_span:
            # If  "data-original-title" is not present, we use the text of the span element
            rating_text = rating_span.text.strip()
            if rating_text == "n.a.":
                rating_elements.append("nincs értékelése")
            else:
                rating_elements.append(rating_text)
    else:
        rating_elements.append("!Rendelkezik negatív értékeléssel!")

    username_elements = [element.find("a").text.strip() for element in soup.find_all("div", class_="uad-misc") if element.find("a")]
    link_elements = [listing_element.find('a')['href'] for listing_element in listing_elements]
    main_picture_elements = soup.find_all("a", class_="uad-image align-self-center")
    main_picture_elements = ["https:" + element.find("img")["src"] for element in main_picture_elements]

    listings = []
    for i in range(len(listing_elements)):
        listings.append({
            "Listing": listing_elements[i].text.strip(),
            "Link": link_elements[i],
            "Price": price_elements[i].text.strip(),
            "Username": username_elements[i],
            "Location": location_elements[i],
            "Seller Ratings": rating_elements[i],
            "Main picture": main_picture_elements[i]
        })
    return listings

def get_detailed_data(link):
    time.sleep(1.05)  # To avoid hitting rate limits
    response = requests.get(link)
    response.raise_for_status()

    html_content = response.text
    soup = BeautifulSoup(html_content, "lxml")

    data = {
        "Description": "",
        "Condition": "",
        "Status": "",
        "Images": [],
        "Avatar": ""
    }

    description_elements = soup.find_all("div", class_="uad-content")
    for description_element in description_elements:
        for br in description_element.find_all("br"):
            br.replace_with("\n")
        data["Description"] = description_element.text.replace("Tetszik", "").strip()[:1023]
        if len(data["Description"]) > 1000:
            data["Description"] = data["Description"][:1000] + "..."
            
    condition_element = soup.find("th", string="Állapot:")
    if condition_element:
        data["Condition"] = condition_element.find_next_sibling("td").text.strip()

    status_element = soup.find("th", string="Szándék:")
    if status_element:
        data["Status"] = status_element.find_next_sibling("td").text.strip()


    avatar_elements = soup.find_all("div", class_="carousel-item active")
    image_elements = soup.find_all("div", class_="carousel-item")

    for avatar_element in avatar_elements:
        data["Avatar"] = "https:" + avatar_element.find("img")["src"]

    for image_element in image_elements:
        image_link = image_element.find("a")
        if image_link and "href" in image_link.attrs:
            image_source = image_link["href"]
            data["Images"].append("https:" + image_source)
            if len(data["Images"]) == 4:
                break


    return data

def send_webhook(data, listings, webhook_url):
    embed_data = {
        "content": None,
        "embeds": [
            {
                "title": listings["Listing"],
                "url": listings["Link"],
                "color": 16750848,
                "fields": [
                    {
                        "name": "> __Ár: __",
                        "value": f"`{listings['Price']}`"
                    },
                    {
                        "name": "> __Lokáció:__",
                        "value": f"`{listings['Location']}`"
                    },
                    {
                        "name": "> __Hirdető:__",
                        "value": f"`{listings['Username']}`"
                    },
                    {
                        "name": "> __Hírdető értékelései:__",
                        "value": f"`{listings['Seller Ratings']}`"
                    },
                    {
                        "name": "> __Leírás:__",
                        "value": f"`{data['Description']}`"
                    },
                    {
                        "name": "> __Állapot:__",
                        "value": f"`{data['Condition']}`"
                    },
                    {
                    "name": "> __Szándék:__",
                    "value": f"`{data['Status']}`"
                    }                    
                ],
                "author": {
                    "name": "Új listing jelent meg az oldalon!",
                    "url": listings["Link"],
                    "icon_url": listings["Main picture"]
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

    time.sleep(0.6)  # To avoid hitting rate limits
    response = requests.post(webhook_url, json=embed_data)
    response.raise_for_status()

def main():
    URL = "https://hardverapro.hu/aprok/mobil/mobil/iphone/iphone_14_2/iphone_14_pro/index.html"
    Webhook_URL = "YOUR DISCORD WEBHOOK URL" # Replace with your Discord webhook URL
    filename = "listings.xlsx"

    existing_listings = load_from_excel(filename)
    if not existing_listings:
        for listing in get_listing_data(BeautifulSoup(requests.get(URL).text, "lxml")):
            detailed_data = get_detailed_data(listing["Link"])
            listing.update(detailed_data)
            existing_listings.append(listing)
    save_to_excel(existing_listings, filename)


    while True:
        response = requests.get(URL)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, "lxml")

        new_listings = get_listing_data(soup)

        for listing in new_listings:
            if listing["Link"] not in [l["Link"] for l in existing_listings]:
                detailed_data = get_detailed_data(listing["Link"])
                listing.update(detailed_data)
                existing_listings.append(listing)
                send_webhook(detailed_data, listing, Webhook_URL)

        save_to_excel(existing_listings, filename)
        time.sleep(15)

if __name__ == "__main__":
    main()