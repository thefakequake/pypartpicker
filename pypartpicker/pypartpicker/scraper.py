import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class Part:

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.url = kwargs.get("url")
        self.type = kwargs.get("type")
        self.price = kwargs.get("price")
        self.image = kwargs.get("image")


class PCPPList:

    def __init__(self, **kwargs):
        self.parts = kwargs.get("parts")
        self.wattage = kwargs.get("wattage")
        self.total = kwargs.get("total")
        self.url = kwargs.get("url")
        self.compatibility = kwargs.get("compatibility")


def make_soup(url):
    # sends a request to the URL
    page = requests.get(url)
    # gets the HTML code for the website and parses it using Python's built in HTML parser
    soup = BeautifulSoup(page.content, 'html.parser')
    # returns the HTML
    return soup


def fetch_list(list_url):

    # checks if its a pcpartpicker list and raises an exception if its not or if the list is empty
    if not "pcpartpicker.com/list/" in list_url or list_url.endswith("/list/"):
        raise Exception(f"'{list_url}' is an invalid PCPartPicker list!")

    # fetches the HTML code for the website
    soup = make_soup(list_url)

    # gets the code with the table containing all the parts
    table = soup.find_all("table", {"class": "xs-col-12"}, limit=1)[0]

    # creates an empty list to put the Part objects inside
    parts = []

    # iterates through every part in the table
    for item in table.find_all('tr', class_="tr__product"):
        # creates a new part object using values obtained from the tables' rows
        part_object = Part(
            name = item.find(class_="td__name").get_text().strip('\n'),
            price = item.find(class_="td__price").get_text().strip('\n').replace("No Prices Available", "None").replace("Price", "").strip('\n'),
            type = item.find(class_="td__component").get_text().strip('\n').strip(),
            image = ("https://" + item.find("img", class_="")["src"]).replace("https://https://", "https://")
        )
        # converts string representation of 'None' to NoneType
        if part_object.price == 'None':
            part_object.price = None
        # checks if the product row has a product URL inside
        if 'href' in str(item.find(class_="td__name")):
            # adds the product URL to the Part object
            part_object.url = "https://" + urlparse(list_url).netloc + item.find(class_="td__name").find("a")["href"].replace("/placeholder-", "")
        # adds the part object to the list
        parts.append(part_object)

    # gets the estimated wattage for the list
    wattage = soup.find(class_="partlist__keyMetric").get_text().replace("Estimated Wattage:", "").strip('\n')

    # gets the total cost for the list
    total_cost = table.find("tr", class_="tr__total tr__total--final").find(class_="td__price").get_text()

    # gets the compatibility notes for the list
    compatibilitynotes = [a.get_text().strip('\n').replace("Note:", "").replace("Warning!", "") for a in soup.find_all("li", class_=["info-message", "warning-message"])]

    # returns a PCPPList object containing all the information
    return PCPPList(parts=parts, wattage=wattage, total=total_cost, url=list_url, compatibility=compatibilitynotes)



def product_search(search_term, **kwargs):

    search_term = search_term.replace(' ', '+')

    # makes sure limit is an integer, raises ValueError if it's not
    if not isinstance(kwargs.get("limit", 20), int):
        raise ValueError("Product limit must be an integer!")

    # checks if the region given is a string, and checks if it is a country code
    if not isinstance(kwargs.get("region", "us"), str) or len(kwargs.get("region", "us")) != 2:
        raise ValueError("Invalid region!")

    # constructs the search URL
    if kwargs.get("region") in ("us", None):
        search_link = f"https://pcpartpicker.com/search/?q={search_term}"
    else:
        search_link = f"https://{kwargs.get('region', '')}.pcpartpicker.com/search/?q={search_term}"

    try:
        # fetches the HTML code for the website
        soup = make_soup(search_link)
    except requests.exceptions.ConnectionError:
        # raises an exception if the region is invalid
        raise ValueError("Invalid region! Max retries exceeded with URL.")

    # checks if the page redirects to a product page
    if soup.find(class_="pageTitle").get_text() != "Product Search":

        # creates a part object with the information from the product page
        part_object = Part(
            name = soup.find(class_="pageTitle").get_text(),
            url = search_link,
            price = None
        )

        # searches for the pricing table
        table = soup.find("table", class_="xs-col-12")

        # loops through every row in the table
        for row in table.find_all("tr"):

            # first conditional statement makes sure its not the top row with the table parameters, second checks if the product is out of stock
            if not "td__availability" in str(row) or "Out of stock" in row.find(class_="td__availability").get_text():

                # skips this iteration
                continue

            # sets the price of the price object to the price
            part_object.price = row.find(class_="td__finalPrice").get_text().strip('\n').strip("+")

            # ends the loop
            break

        # returns the part object
        return [part_object]

    # gets the section of the website's code with the search results
    section = soup.find("section", class_="search-results__pageContent")

    # creates an empty list for the part objects to be stored in
    parts = []

    # iterates through all the HTML elements that match the given the criteria
    for product in section.find_all("ul", class_="list-unstyled"):
        # extracts the product data from the HTML code and creates a part object with that information
        part_object = Part(
            name = product.find("p", class_="search_results--link").get_text().strip(),
            url = product.find("p", class_="search_results--link").find("a", href=True)["href"],
            image = ("https://" + product.find("img")["src"].strip('/')).replace("https://https://", "https://")
        )
        try:
            part_object.price = product.find(class_="product__link product__link--price").get_text()
        except AttributeError:
            part_object.price = None

        # adds the part object to the list
        parts.append(part_object)

    # returns the part objects
    return parts[:kwargs.get("limit", 20)]