from requests_html import HTML
from .part import Part, Rating, Vendor, Price
from .urls import BASE_PRODUCT_PATH
from .regex import *
from requests import Response


class Scraper:
    def __init__(self, region: str = "us"):
        self.region = region.lower()

    def __get_base_url(self, override_region: str = None) -> str:
        region = self.region if override_region is None else override_region

        if region == "us":
            return f"https://pcpartpicker.com"

        return f"https://{region.lower()}.pcpartpicker.com"

    def prepare_part_url(self, id_url: str, region: str = None) -> str:
        match = PRODUCT_URL_RE.match(id_url)
        if match is None:
            url = ID_RE.match(id_url)
            id_url = url.group(1)
        else:
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
                if "FREE" in shipping_raw.text or shipping_raw.text.strip() == ""
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
            ].price.total

        # Part URL
        url = html.find('head meta[property="og:url"]', first=True).attrs["content"]

        return Part(
            name=name,
            type=type,
            image_urls=image_urls,
            url=url,
            cheapest_price=cheapest_price,
            in_stock=in_stock,
            vendors=vendors,
            rating=rating,
            specs=specs,
        )
