import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class Part:

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.url = kwargs.get("url")
        self.type = kwargs.get("type")
        self.price = kwargs.get("price")

class PCPPList:

    def __init__(self, **kwargs):
        self.parts = kwargs.get("parts")
        self.wattage = kwargs.get("wattage")
        self.total = kwargs.get("total")

def make_soup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


def fetch_parts(list_url):

    if not "pcpartpicker" in list_url:
        raise Exception(f"'{list_url}' is an invalid PCPartPicker list!")

    soup = make_soup(list_url)

    table = soup.find_all("table", {"class": "xs-col-12"}, limit=1)[0]

    parts = []

    for item in table.find_all('tr', class_="tr__product"):
        part_object = Part(
            name = item.find(class_="td__name").get_text().strip('\n'),
            price = item.find(class_="td__price").get_text().strip('\n').replace("No Prices Available", "None").replace("Price", "").strip('\n'),
            type = item.find(class_="td__component").get_text().strip('\n').strip()
        )
        if part_object.price == 'None':
            part_object.price = None
        if 'href' in str(item.find(class_="td__name")):
            part_object.url = "https://" + urlparse(list_url).netloc + item.find(class_="td__name").find("a")["href"].replace("/placeholder-", "")
        parts.append(part_object)
    wattage = soup.find(class_="partlist__keyMetric").get_text().replace("Estimated Wattage:", "").strip('\n')
    total_cost = table.find("tr", class_="tr__total tr__total--final").find(class_="td__price").get_text()
    return PCPPList(parts=parts, wattage=wattage, total=total_cost)

    # for a in soup.find_all(class_='td__name'):
    #     if 'From parametric selection:' in a.get_text():
    #         part_names.append(a.get_text().split('From parametric selection:')[0].replace('\n', ''))
    #     elif 'From parametric filter:' in a.get_text():
    #         part_names.append(a.get_text().split('From parametric filter:')[0].replace('\n', ''))
    #     else:
    #         part_names.append(a.get_text().replace('\n', ''))
    #     if 'a href=' in str(a) and not '#view_custom_part' in str(a):
    #         elements = str(a).split('"')
    #         for element in elements:
    #             if element.startswith("/product/"):
    #                 part_urls.append(f"{list_url.split('com')[0]}com{element}".replace("/placeholder-", ""))
    #     else:
    #         part_urls.append(None)
    #
    # part_types = [a.get_text().replace('\n', '') for a in soup.find_all(class_='td__component')]
    #
    # try:
    #     wattage = soup.find(class_='partlist__keyMetric').get_text().replace('\n', '').replace("Estimated Wattage:", '')
    # except (AttributeError, IndexError):
    #     wattage = None
    #
    # prices = [a.get_text().replace("Price", "") for a in soup.find_all(class_='td__price')]
    #
    # if len(prices) == 0: prices = None
    #
    # part_objects = []
    #
    # page_title = soup.find(class_="pageTitle").get_text()

    # for i in range(len(part_names)):
    #     part_objects.append(Part(
    #         name = part_names[i],
    #         type = part_types[i],
    #         url = part_urls[i],
    #         price = prices[i] if i < len(prices) else None
    #     ))
    # return part_objects