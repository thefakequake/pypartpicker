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


def fetch_parts(list_url):

    # checks if its a pcpartpicker list and raises an exception if its not or if the list is empty
    if not "pcpartpicker.com/list/" in list_url or list.url.endswith("/list/"):
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
            type = item.find(class_="td__component").get_text().strip('\n').strip()
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