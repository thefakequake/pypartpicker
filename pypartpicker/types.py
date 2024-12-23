from typing import Optional


class Price:
    def __init__(
        self,
        base: Optional[float] = None,
        discounts: Optional[float] = None,
        shipping: Optional[float] = None,
        tax: Optional[float] = None,
        total: Optional[float] = None,
        currency: Optional[str] = None,
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
        if self.currency is None:
            return "<No Prices Available>"
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


class User:
    def __init__(
        self,
        username: str,
        avatar_url: str,
        profile_url: str,
    ):
        self.username = username
        self.avatar_url = avatar_url
        self.profile_url = profile_url


class Review:
    def __init__(
        self,
        author: User,
        points: int,
        stars: int,
        created_at: str,
        content: str,
        build_name: Optional[str] = None,
        build_url: Optional[str] = None,
    ):
        self.author = author
        self.points = points
        self.stars = stars
        self.created_at = created_at
        self.content = content
        self.build_name = build_name
        self.build_url = build_url


class PartReviewsResponse:
    def __init__(self, reviews: list[Review], page: int, total_pages: int):
        self.reviews = reviews
        self.page = page
        self.total_pages = total_pages


class Part:
    def __init__(
        self,
        name: str,
        type: str,
        image_urls: Optional[list[str]],
        url: Optional[str],
        cheapest_price: Optional[Price],
        in_stock: Optional[bool],
        vendors: Optional[list[Vendor]] = None,
        rating: Optional[Rating] = None,
        specs: Optional[dict[str, str]] = None,
        reviews: Optional[list[Review]] = None,
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
        self.reviews = reviews

    def __repr__(self):
        return f"<Part {self.name}>"


class PartList:
    def __init__(
        self,
        parts: list[Part],
        url: str,
        estimated_wattage: float,
        total_price: float,
        currency: str,
    ):
        self.parts = parts
        self.url = url
        self.estimated_wattage = estimated_wattage
        self.total_price = total_price
        self.currency = currency


class PartSearchResult:
    def __init__(self, parts: list[Part], page: int, total_pages: int):
        self.parts = parts
        self.page = page
        self.total_pages = total_pages
