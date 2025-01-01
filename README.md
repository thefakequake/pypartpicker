# pypartpicker

A PCPartPicker data extractor for Python.

### Features:

- Fetch product information, specs, pricing and reviews
- Fetch part lists
- Utilise PCPartPicker's built in search functionality
- Scraping countermeasures out of the box via [requests-html](https://github.com/psf/requests-html>)
- Support for all regions
- Customisable scraping

# Table of Contents

- [Installation](#installation)
- [Examples](#examples)
- [Documentation](#documentation)
  - [Client](#client)
  - [Part](#part)
  - [PartList](#part-list)
  - [PartSearchResult](#part-search-result)
  - [PartReviewsResult](#part-reviews-result)
  - [Price](#price)
  - [Vendor](#vendor)
  - [Rating](#rating)
  - [Review](#review)
  - [User](#user)
  - [Supported Regions](#regions)
  - [Supported Product Types](#types)
- [FAQs](#faqs)

# Installation

```bash
$ pip install pypartpicker
```

# Note

Due to [pyppeteer](https://github.com/pyppeteer/pyppeteer) your first use of the library may install a chromium browser for JS rendering.

This is only done once. If you would like to disable this feature entirely, use the `no_js=True` option in the Client constructor.

# Examples

Fetch a product:

```py
import pypartpicker

pcpp = pypartpicker.Client()
part = pcpp.get_part("https://pcpartpicker.com/product/fN88TW")

for spec, value in part.specs.items():
    print(f"{spec}: {value}")

print(part.cheapest_price)
```

Search parts with pagination:

```py
import pypartpicker

pcpp = pypartpicker.Client()
page = 1

while True:
    result = pcpp.get_part_search("ryzen 5", region="uk", page=page)

    for part in result.parts:
        print(part.name)

    page += 1
    if page > result.total_pages:
        break
```

Fetch a product (async):

```py
import pypartpicker
import asyncio


async def get_parts():
    async with pypartpicker.AsyncClient() as pcpp:
        part = await pcpp.get_part("https://pcpartpicker.com/product/fN88TW")

    for spec, value in part.specs.items():
        print(f"{spec}: {value}")


asyncio.run(get_parts())
```

Proxy rotation w/ response_retriever override:

```py
import pypartpicker
import requests_html # requires requests-html and pysocks to be installed
from itertools import cycle

# replace with own list of proxies
list_proxy = [
    "socks5://Username:Password@IP1:20000",
    "socks5://Username:Password@IP2:20000",
    "socks5://Username:Password@IP3:20000",
    "socks5://Username:Password@IP4:20000",
]

proxy_cycle = cycle(list_proxy)
session = requests_html.HTMLSession()


def response_retriever(url):
    proxy = next(proxy_cycle)
    return session.get(url, proxies={"http": proxy, "https": proxy})


client = pypartpicker.Client(response_retriever=response_retriever)

res = client.get_part_search("cpu")
for result in res.parts:
    part = client.get_part(result.url)
    print(part.specs)
```

# Documentation

<h2 id="client">Client</h2>

Represents a client for interacting with parts-related data and making HTTP requests.

### Options

- **`max_retries`**: `int` – The maximum number of retries for requests. Default is `3`.
- **`retry_delay`**: `int` – The delay between retries in seconds. Default is `0`.
- **`cookies`**: `Optional[dict]` – Cookies to include in requests.
- **`response_retriever`**: `Optional[Callable]` – A custom function to perform a request, overriding the default one.
  Can be used to implement proxy rotation and custom scraping measures.
- **`no_js`**: `bool` – Disables pyppeteer JS rendering. Default is `False`.

---

### Methods

#### `get_part(id_url: str, region: str = None) -> Part`

Fetches a single part by its URL/ID and region.

- **Parameters**:

  - **`id_url`**: `str` – The part ID or URL of the part to retrieve.
  - **`region`**: `Optional[str]` – The region for the part data.

- **Returns**: [`Part`](#part) – The part details.

---

#### `get_part_list(id_url: str, region: str = None) -> PartList`

Fetches a part list by its URL/ID and region.

- **Parameters**:

  - **`id_url`**: `str` – The part list ID or URL of the part list to retrieve.
  - **`region`**: `Optional[str]` – The region for the part list data.

- **Returns**: [`PartList`](#part-list) – The part list details.

---

#### `get_part_search(query: str, page: int = 1, region: Optional[str] = None) -> PartSearchResult`

Searches for parts using PCPartPicker's search functionality.

- **Parameters**:

  - **`query`**: `str` – The search query string.
  - **`page`**: `int` – The page number to fetch. Default is `1`.
  - **`region`**: `Optional[str]` – The region for the search results.

- **Returns**: [`PartSearchResult`](#part-search-result) – The search results for parts.

---

#### `get_part_reviews(id_url: str, page: int = 1, rating: Optional[int] = None) -> PartReviewsResult`

Fetches reviews for a specific part.

- **Parameters**:

  - **`id_url`**: `str` – The part ID or URL of the part to retrieve reviews for.
  - **`page`**: `int` – The page number to fetch. Default is `1`.
  - **`rating`**: `Optional[int]` – Filter reviews by a specific star rating.

- **Returns**: [`PartReviewsResult`](#part-reviews-result) – The reviews for the specified part.

---

<!--
#### `get_parts(product_path: str, page: int = 1, region: Optional[str] = None, compatible_with: Optional[str] = None) -> PartSearchResult`

Fetches parts of a specific product type.

- **Parameters**:

  - **`product_path`**: `str` – The [product path](#product-path) to retrieve parts for.
  - **`page`**: `int` – The page number to fetch. Default is `1`.
  - **`region`**: `Optional[str]` – The region for the part data.
  - **`compatible_with`**: `Optional[str]` – Filter by compatibility with a specific part URL/ID.

- **Returns**: [`PartSearchResult`](#part-search-result) – The parts matching the query. -->

### Exceptions

- **`CloudflareException`** – Raised when the request fails due to Cloudflare protection after the maximum retries.
- **`RateLimitException`** – Raised when the request encounters a PCPartPicker rate limit issue.

---

<h2 id="client">AsyncClient</h2>

Same methods and options as Client except called with `await`.

## Types

<h3 id="price">Price</h3>

Represents the pricing details of a product.

- **`base`**: `Optional[float]` – The base price of the item.
- **`discounts`**: `Optional[float]` – Any discounts applied to the item.
- **`shipping`**: `Optional[float]` – Shipping costs associated with the item.
- **`tax`**: `Optional[float]` – Taxes applied to the item.
- **`total`**: `Optional[float]` – The total price after applying all factors.
- **`currency`**: `Optional[str]` – The currency of the price.

---

<h3 id="vendor">Vendor</h3>

Represents a vendor offering a product.

- **`name`**: `str` – The name of the vendor.
- **`logo_url`**: `str` – The URL to the vendor's logo image.
- **`in_stock`**: `bool` – Whether the product is in stock.
- **`price`**: [`Price`](#price) – The price details for the product.
- **`buy_url`**: `str` – The vendor URL to purchase the product.

---

<h3 id="rating">Rating</h3>

Represents the rating of a product.

- **`stars`**: `int` – The number of stars given by reviewers.
- **`count`**: `int` – The total number of ratings received.
- **`average`**: `float` – The average rating value.

---

<h3 id="user">User</h3>

Represents a user who interacts with reviews.

- **`username`**: `str` – The username of the user.
- **`avatar_url`**: `str` – The URL to the user's avatar image.
- **`profile_url`**: `str` – The URL to the user's profile.

---

<h3 id="review">Review</h3>

Represents a review for a product.

- **`author`**: [`User`](#user) – The user who wrote the review.
- **`points`**: `int` – The number of points given to the review.
- **`stars`**: `int` – The star rating given in the review.
- **`created_at`**: `str` – The timestamp when the review was created.
- **`content`**: `str` – The textual content of the review.
- **`build_name`**: `Optional[str]` – The name of the build associated with the review.
- **`build_url`**: `Optional[str]` – The URL to the build associated with the review.

---

<h3 id="part-reviews-result">PartReviewsResult</h3>

Represents the result of a paginated query for part reviews.

- **`reviews`**: `list` of [`Review`](#review) – A list of reviews for a product.
- **`page`**: `int` – The current page of results.
- **`total_pages`**: `int` – The total number of pages available.

---

<h3 id="part">Part</h3>

Represents a part from a product page, part list or search page.

- **`name`**: `str` – The name of the part.
- **`type`**: `str` – The type or category of the part.
- **`image_urls`**: `Optional[list[str]]` – Image URLs of the part.
- **`url`**: `Optional[str]` – The part's main product URL.
- **`cheapest_price`**: `Optional` of [`Price`](#price) – The cheapest price for the part.
- **`in_stock`**: `Optional[bool]` – Whether the part is currently in stock.
- **`vendors`**: `Optional[list` of [`Vendor`](#vendor)`]` – A list of vendors offering the part.
- **`rating`**: `Optional` of [`Rating`](#rating) – The rating details for the part.
- **`specs`**: `Optional[dict[str, str]]` – A dictionary of specifications for the part.
- **`reviews`**: `Optional[list` of [`Review`](#review)`]` – A list of reviews for the part.

---

<h3 id="part-list">PartList</h3>

Represents a list of parts for a system or build.

- **`parts`**: `list` of [`Part`](#part) – A list of parts in the build (only partial data).
- **`url`**: `str` – The URL for the part list.
- **`estimated_wattage`**: `float` – The power consumption of the build, measured in watts.
- **`total_price`**: `float` – The total price of the build.
- **`currency`**: `str` – The currency used for pricing.

---

<h3 id="part-search-result">PartSearchResult</h3>

Represents the result of a paginated query for parts.

- **`parts`**: `list` of [`Part`](#part) – A list of parts matching the search query (only partial data).
- **`page`**: `int` – The current page of results.
- **`total_pages`**: `int` – The total number of pages available.

<h2 id="regions">Supported Regions</h2>

- **Australia**: `au`
- **Austria**: `at`
- **Belgium**: `be`
- **Canada**: `ca`
- **Czech Republic**: `cz`
- **Denmark**: `dk`
- **Finland**: `fi`
- **France**: `fr`
- **Germany**: `de`
- **Hungary**: `hu`
- **Ireland**: `ie`
- **Italy**: `it`
- **Netherlands**: `nl`
- **New Zealand**: `nz`
- **Norway**: `no`
- **Portugal**: `pt`
- **Romania**: `ro`
- **Saudi Arabia**: `sa`
- **Slovakia**: `sk`
- **Spain**: `es`
- **Sweden**: `se`
- **United Kingdom**: `uk`
- **United States**: `us`

<h2 id="product-path">Supported Product Types</h2>

```py
PRODUCT_KEYBOARD_PATH = "keyboard"
PRODUCT_SPEAKERS_PATH = "speakers"
PRODUCT_MONITOR_PATH = "monitor"
PRODUCT_THERMAL_PASTE_PATH = "thermal-paste"
PRODUCT_VIDEO_CARD_PATH = "video-card"
PRODUCT_CASE_FAN_PATH = "case-fan"
PRODUCT_OS_PATH = "os"
PRODUCT_CPU_COOLER_PATH = "cpu-cooler"
PRODUCT_FAN_CONTROLLER_PATH = "fan-controller"
PRODUCT_UPS_PATH = "ups"
PRODUCT_WIRED_NETWORK_CARD_PATH = "wired-network-card"
PRODUCT_MEMORY_PATH = "memory"
PRODUCT_HEADPHONES_PATH = "headphones"
PRODUCT_SOUND_CARD_PATH = "sound-card"
PRODUCT_INTERNAL_HARD_DRIVE_PATH = "internal-hard-drive"
PRODUCT_MOUSE_PATH = "mouse"
PRODUCT_WIRELESS_NETWORK_CARD_PATH = "wireless-network-card"
PRODUCT_POWER_SUPPLY_PATH = "power-supply"
PRODUCT_WEBCAM_PATH = "webcam"
PRODUCT_MOTHERBOARD_PATH = "motherboard"
PRODUCT_EXTERNAL_HARD_DRIVE_PATH = "external-hard-drive"
PRODUCT_OPTICAL_DRIVE_PATH = "optical-drive"
PRODUCT_CASE_PATH = "case"
PRODUCT_CPU_PATH = "cpu"
```
<h2 id="faqs">FAQs</h2>

**Chromium Errors**

If `[INFO]: Downloading Chromium` errors are encountered, find your `__init__.py` file located in `C:\Users\yourusername\AppData\Local\Programs\Python\Python3XX\Lib\site-packages\pyppeteer`, and edit line 20 from `__chromium_revision__ = '1181205'` to `__chromium_revision__ = '1263111'`
