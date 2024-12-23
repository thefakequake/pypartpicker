from typing import Optional
from requests_html import HTML
import urllib.parse
from .part import Part, Rating, Vendor, Price, PartList, PartSearchResult
from .urls import *
from .regex import *
from requests import Response


class Scraper:
    def __init__(self):
        pass

    def __get_base_url(self, region: str) -> str:
        if region == "us":
            return "https://pcpartpicker.com"

        return f"https://{region}.pcpartpicker.com"

    def is_cloudflare(self, res: Response) -> bool:
        return res.html.find("title", first=True).text == "Just a moment..."

    def is_rate_limit(self, res: Response) -> bool:
        title = res.html.find(".pageTitle", first=True)
        if title is None:
            return False
        return title.text == "Verification"

    def prepare_part_url(self, id_url: str, region: str = None) -> str:
        match = PRODUCT_URL_RE.match(id_url)
        if match is None:
            url = ID_RE.match(id_url)
            if url is None:
                raise ValueError("Invalid pcpartpicker product URL or ID.")

            id_url = url.group(1)
            region = "us"
        else:
            region = "us" if match.group(2) is None else match.group(2)[:-1]
            id_url = match.group(3)

        if id_url is None:
            raise ValueError("Invalid pcpartpicker product URL or ID.")

        return self.__get_base_url(region) + BASE_PRODUCT_PATH + id_url

    def parse_part(self, res: Response) -> Part:
        html: HTML = res.html
        title_container = html.find(".wrapper__pageTitle", first=True)
        sidebar = html.find(".sidebar-content", first=True)

        # Part name and type
        type = title_container.find(".breadcrumb", first=True).text
        name = title_container.find(".pageTitle", first=True).text

        # Rating
        rating = None
        star_container = title_container.find(".product--rating", first=True)
        if star_container is not None:
            stars = (
                len(star_container.find(".shape-star-full"))
                + len(star_container.find(".shape-star-half")) * 0.5
            )
            rating_info = PRODUCT_RATINGS_RE.match(
                title_container.find("section div:has(ul)", first=True).text
            )
            count = rating_info.group(1)
            average = rating_info.group(2)
            rating = Rating(stars, int(count), float(average))

        # Specs
        specs = {}
        for spec in sidebar.find(".group--spec"):
            spec_title = spec.find(".group__title", first=True).text
            spec_value = spec.find(".group__content", first=True).text
            specs[spec_title] = spec_value

        # Images
        image_urls = []
        thumbnails = sidebar.find(".product__image-2024-thumbnails", first=True)
        if thumbnails is None:
            image_urls.append(
                "https"
                + sidebar.find(".product__image-2024 img", first=True).attrs["src"]
            )
        else:
            for image in thumbnails.find("img"):
                image_base_url = "https:" + image.attrs["src"].split(".256p.jpg")[0]
                image_urls.append(image_base_url + ".1600.jpg")

        # Vendors
        vendors = []
        for row in html.find("#prices table tbody tr:not(.tr--noBorder)"):
            vendor_image = row.find(".td__logo img", first=True)
            logo_url = "https:" + vendor_image.attrs["src"]
            vendor_name = vendor_image.attrs["alt"]

            # Vendor price
            base_price_raw = row.find(".td__base", first=True).text
            base_price = DECIMAL_RE.search(base_price_raw).group()
            currency = base_price_raw.replace(base_price, "").strip()

            # Discounts, shipping, tax and total price
            promo = (
                row.find(".td__promo", first=True).text.replace(currency, "").strip()
            )
            if promo == "":
                promo = "0"

            shipping_raw = row.find(".td__shipping", first=True)
            shipping = (
                0
                if "FREE" in shipping_raw.text
                or shipping_raw.text.strip() == ""
                or shipping_raw.find("img", first=True) is not None
                else DECIMAL_RE.search(shipping_raw.text).group()
            )
            tax = row.find(".td__tax", first=True).text.replace(currency, "").strip()
            if tax == "":
                tax = "0"

            final = row.find(".td__finalPrice a", first=True)
            total_price = final.text.replace(currency, "").strip().removesuffix("+")

            # Availability and buy url
            in_stock = row.find(".td__availability--inStock", first=True) is not None
            buy_url = final.attrs["href"]

            vendors.append(
                Vendor(
                    name=vendor_name,
                    logo_url=logo_url,
                    in_stock=in_stock,
                    price=Price(
                        base=float(base_price),
                        discounts=float(promo),
                        shipping=float(shipping),
                        tax=float(tax),
                        total=float(total_price),
                        currency=currency,
                    ),
                    buy_url=buy_url,
                )
            )

        cheapest_price = None
        in_stock = False

        available_vendors = list(filter(lambda v: v.in_stock, vendors))
        if len(available_vendors) > 0:
            in_stock = True
            cheapest_price = sorted(available_vendors, key=lambda v: v.price.total)[
                0
            ].price

        return Part(
            name=name,
            type=type,
            image_urls=image_urls,
            url=res.url,
            cheapest_price=cheapest_price,
            in_stock=in_stock,
            vendors=vendors,
            rating=rating,
            specs=specs,
        )

    def prepare_part_list_url(self, id_url: str, region: str = None) -> str:
        match = PART_LIST_URL_RE.match(id_url)
        override_region = region
        if match is None:
            url = ID_RE.match(id_url)
            if url is None:
                raise ValueError("Invalid pcpartpicker part list URL or ID.")

            id_url = url.group(1)
            region = "us"
        else:
            region = "us" if match.group(2) is None else match.group(2)[:-1]
            id_url = match.group(3)

        if override_region is not None:
            region = override_region

        if id_url is None:
            raise ValueError("Invalid pcpartpicker part list URL or ID.")

        return self.__get_base_url(region) + BASE_PART_LIST_PATH + id_url

    def parse_part_list(self, res: Response) -> PartList:
        html: HTML = res.html
        wrapper = html.find(".partlist__wrapper", first=True)
        part_list = html.find(".partlist", first=True)

        estimated_wattage = (
            wrapper.find(".partlist__keyMetric", first=True)
            .text.removeprefix("Estimated Wattage:")
            .strip()
        )

        # Parts
        parts = []
        for row in part_list.find("table tbody tr.tr__product"):
            type = row.find(".td__component", first=True).text.strip()

            image = row.find(".td__image img", first=True)
            image_urls = []
            if image is not None:
                image_urls = [image.attrs["src"]]

            name = "\n".join(
                filter(
                    lambda s: len(s) > 0,
                    (
                        row.find(".td__name", first=True)
                        .text.replace("From parametric selection:", "")
                        .strip()
                    ).split("\n"),
                )
            )
            part_link = row.find(".td__name a", first=True)
            url = None
            if part_link is not None:
                url = (
                    "https://"
                    + urllib.parse.urlparse(res.url).netloc
                    + part_link.attrs["href"]
                )

            base_price_raw = (
                row.find(".td__base", first=True).text.replace("Base", "").strip()
            )
            base_price = (
                None
                if base_price_raw == ""
                else DECIMAL_RE.search(base_price_raw).group()
            )
            currency = (
                None if base_price is None else base_price_raw.replace(base_price, "")
            )

            vendors = []
            in_stock = False
            total_price = None

            # Price parsing is painful... they're often missing or contain weird invisible text artefacts
            if base_price is not None:
                promo_raw = row.find(".td__promo", first=True).text
                promo = float(
                    0
                    if currency not in promo_raw
                    else DECIMAL_RE.search(promo_raw).group()
                )

                shipping_raw = row.find(".td__shipping", first=True).text.strip()
                shipping = float(
                    0
                    if "FREE" in shipping_raw
                    or shipping_raw == ""
                    or currency not in shipping_raw
                    else DECIMAL_RE.search(shipping_raw).group()
                )

                tax_raw = row.find(".td__tax", first=True).text.strip()
                tax = float(
                    0
                    if tax_raw == "" or currency not in tax_raw
                    else DECIMAL_RE.search(tax_raw).group()
                )

                total_price = float(
                    DECIMAL_RE.search(row.find(".td__price", first=True).text).group()
                )
                in_stock = True

                vendor = row.find(".td__where a", first=True)
                buy_url = vendor.attrs["href"]
                vendor_logo = vendor.find("img", first=True)
                vendor_name = vendor_logo.attrs["alt"]
                logo_url = "https:" + vendor_logo.attrs["src"]

                vendors = [
                    Vendor(
                        name=vendor_name,
                        logo_url=logo_url,
                        in_stock=in_stock,
                        price=Price(
                            None if base_price is None else float(base_price),
                            None if promo is None else -promo,
                            shipping,
                            tax,
                            total_price,
                            currency,
                        ),
                        buy_url=buy_url,
                    )
                ]
            else:
                total_price_raw = row.find(".td__price", first=True).text.strip()
                if (
                    "No Prices Available" not in total_price_raw
                    and total_price_raw != ""
                ):
                    total_price = DECIMAL_RE.search(total_price_raw).group()
                    currency = (
                        total_price_raw.replace(total_price, "")
                        .replace("Price", "")
                        .strip()
                    )
                    total_price = float(total_price)

            parts.append(
                Part(
                    name,
                    type,
                    image_urls,
                    url,
                    (
                        Price(
                            base=base_price,
                            discounts=0,
                            shipping=0,
                            tax=0,
                            total=total_price,
                            currency=currency,
                        )
                        if total_price is not None
                        else (
                            None
                            if vendors == []
                            else None if currency is None else vendors[0].price
                        )
                    ),
                    in_stock,
                    vendors=vendors,
                    rating=None,
                    specs=None,
                )
            )

        currency = None
        total_price = 0
        total = part_list.find(".tr__total--final .td__price", first=True)
        if total is not None:
            total_price = DECIMAL_RE.search(total.text).group()
            currency = total.text.replace(total_price, "").strip()

        return PartList(
            parts=parts,
            url=res.url,
            estimated_wattage=estimated_wattage,
            total_price=float(total_price),
            currency=currency,
        )

    def prepare_search_url(self, query: str, page: int, region: Optional[str]):
        return (
            self.__get_base_url("us" if region is None else region)
            + BASE_SEARCH_PATH
            + f"?q={urllib.parse.quote(query)}&page={page}"
        )

    def parse_part_search(self, res: Response) -> PartSearchResult:
        html: HTML = res.html

        # Case for which the search redirects to the product page
        if html.find(".pageTitle", first=True).text != "Product Search":
            return [self.parse_part(res)]

        results = []
        for result in html.find(".search-results__pageContent li"):
            image_url = (
                "https:"
                + result.find(".search_results--img img", first=True).attrs["src"]
            )
            link = result.find(".search_results--link a", first=True)

            url = (
                "https://" + urllib.parse.urlparse(res.url).netloc + link.attrs["href"]
            )
            name = link.text

            price = result.find(".search_results--price", first=True).text.strip()
            cheapest_price = None
            if price != "":
                total = DECIMAL_RE.search(price).group()
                currency = price.replace(total, "").strip()
                cheapest_price = Price(
                    base=None,
                    discounts=None,
                    shipping=None,
                    tax=None,
                    total=total,
                    currency=currency,
                )

            type = name.split(" ")[-2]
            if type == "Processor":
                type = "CPU"

            results.append(
                Part(
                    name=name,
                    type=None,
                    image_urls=[image_url],
                    url=url,
                    cheapest_price=cheapest_price,
                    in_stock=cheapest_price is not None,
                    vendors=None,
                    rating=None,
                    specs=None,
                )
            )

        pagination = html.find("#module-pagination", first=True)

        current_page = int(pagination.find(".pagination--current", first=True).text)
        total_pages = int(pagination.find("li:last-child", first=True).text)

        return PartSearchResult(
            parts=results, page=current_page, total_pages=total_pages
        )
