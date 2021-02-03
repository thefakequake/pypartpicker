import requests
from bs4 import BeautifulSoup


class Part:

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.url = kwargs.get("url")
        self.type = kwargs.get("type")
        self.price = kwargs.get("price")


def make_soup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


def fetch_parts(list_url):

    soup = make_soup(list_url)

    part_names = []
    part_types = []
    part_urls = []

    for a in soup.find_all(class_='td__name'):
        if 'From parametric selection:' in a.get_text():
            part_names.append(a.get_text().split('From parametric selection:')[0].replace('\n', ''))
        elif 'From parametric filter:' in a.get_text():
            part_names.append(a.get_text().split('From parametric filter:')[0].replace('\n', ''))
        else:
            part_names.append(a.get_text().replace('\n', ''))
        if 'a href=' in str(a) and not '#view_custom_part' in str(a):
            elements = str(a).split('"')
            for element in elements:
                if element.startswith("/product/"):
                    part_urls.append(f"{list_url.split('com')[0]}com{element}")
        else:
            part_urls.append(None)

    part_types = [a.get_text().replace('\n', '') for a in soup.find_all(class_='td__component')]

    try:
        wattage = soup.find(class_='partlist__keyMetric').get_text().replace('\n', '').replace("Estimated Wattage:", '')
    except (AttributeError, IndexError):
        wattage = None

    prices = [a.get_text() for a in soup.find_all(class_='td__price')]

    if len(prices) == 0: prices = None

    part_objects = []

    page_title = soup.find(class_="pageTitle").get_text()

    for i in range(len(part_names)):
        part_objects.append(Part(
            name = part_names[i],
            type = part_types[i],
            url = part_urls[i],
            price = prices[i] if i < len(prices) else None
        ))
    return part_objects