from typing import Optional


class Price:
    def __init__(
        self,
        base: float,
        discounts: float,
        shipping: float,
        tax: float,
        total: float,
        currency: str,
    ):
        self.base = base
        self.discounts = discounts
        self.shipping = shipping
        self.tax = tax
        self.total = total
        self.currency = currency

    def __repr__(self):
        return f"<Price total={self.total} currency={self.currency}>"

    def __str__(self):
        return self.currency + str(self.total)


class Vendor:
    def __init__(
        self, name: str, logo_url: str, in_stock: bool, price: Price, buy_url: str
    ):
        self.name = name
        self.logo_url = logo_url
        self.in_stock = in_stock
        self.price = price
        self.buy_url = buy_url


class Rating:
    def __init__(self, stars: int, count: int, average: float):
        self.stars = stars
        self.count = count
        self.average = average

    def __repr__(self):
        return f"<Rating stars={self.stars} count={self.count} average={self.average}>"


class Part:
    def __init__(
        self,
        name: str,
        type: str,
        image_urls: list[str],
        url: str,
        cheapest_price: float,
        in_stock: bool,
        vendors: Optional[list[Vendor]] = None,
        rating: Optional[Rating] = None,
        specs: Optional[dict[str, str]] = None,
    ):
        self.name = name
        self.type = type
        self.image_urls = image_urls
        self.url = url
        self.cheapest_price = cheapest_price
        self.in_stock = in_stock
        self.vendors = vendors
        self.rating = rating
        self.specs = specs

    def __repr__(self):
        return f"<Part {self.name}>"
