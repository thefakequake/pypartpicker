from .scraper import Scraper
from .types import Part, PartList, PartSearchResult, PartReviewsResult
from .errors import CloudflareException, RateLimitException
from requests import Response
from requests_html import HTMLSession, AsyncHTMLSession
from typing import Coroutine, Optional
import time


class Client:
    def __init__(self, max_retries=3, retry_delay=0):
        self.__scraper = Scraper()
        self.__session = HTMLSession()
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def __get_response(self, url: str, retries=0) -> Response:
        if retries >= self.max_retries:
            raise CloudflareException(f"Request to {url} failed, max retries exceeded.")

        res = self.__session.get(url)

        # Check if we are being Cloudflare checked
        if self.__scraper.is_cloudflare(res):
            res.html.render()

            if self.__scraper.is_cloudflare(res):
                time.sleep(self.retry_delay)
                return self.__get_response(url, retries + 1)
        elif self.__scraper.is_rate_limit(res):
            raise RateLimitException(f"PCPP rate limit encountered: {url}")

        return res

    def get_part(self, id_url: str, region: str = None) -> Part:
        url = self.__scraper.prepare_part_url(id_url, region)
        res = self.__get_response(url)
        return self.__scraper.parse_part(res)

    def get_part_list(self, id_url: str, region: str = None) -> PartList:
        url = self.__scraper.prepare_part_list_url(id_url, region)
        res = self.__get_response(url)
        return self.__scraper.parse_part_list(res)

    def get_part_search(
        self, query: str, page: int = 1, region: Optional[str] = None
    ) -> PartSearchResult:
        url = self.__scraper.prepare_search_url(query, page, region)
        res = self.__get_response(url)
        return self.__scraper.parse_part_search(res)

    def get_part_reviews(
        self, id_url: str, page: int = 1, rating: Optional[int] = None
    ) -> PartReviewsResult:
        url = self.__scraper.prepare_part_reviews_url(id_url, page, rating)
        res = self.__get_response(url)
        return self.__scraper.parse_reviews(res)


class AsyncClient:
    def __init__(self, max_retries=3, retry_delay=0):
        self.__scraper = Scraper()
        self.__session = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def __aenter__(self):
        self.__session = AsyncHTMLSession()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__session.close()

    async def __get_response(
        self, url: str, retries=0
    ) -> Coroutine[None, None, Response]:
        if retries >= self.max_retries:
            raise CloudflareException(f"Request to {url} failed, max retries exceeded.")

        res = await self.__session.get(url)

        # Check if we are being Cloudflare checked
        if self.__scraper.is_cloudflare(res):
            await res.html.arender()

            if self.__scraper.is_cloudflare(res):
                time.sleep(self.retry_delay)
                return self.__get_response(url, retries + 1)
        elif self.__scraper.is_rate_limit(res):
            raise RateLimitException(f"PCPP rate limit encountered: {url}")

        return res

    async def get_part(
        self, id_url: str, region: str = None
    ) -> Coroutine[None, None, Part]:
        url = self.__scraper.prepare_part_url(id_url, region)
        res = await self.__get_response(url)
        return self.__scraper.parse_part(res)

    async def get_part_list(
        self, id_url: str, region: str = None
    ) -> Coroutine[None, None, PartList]:
        url = self.__scraper.prepare_part_list_url(id_url, region)
        res = await self.__get_response(url)
        return self.__scraper.parse_part_list(res)

    async def get_part_search(
        self, query: str, page: int = 1, region: Optional[str] = None
    ) -> Coroutine[None, None, PartSearchResult]:
        url = self.__scraper.prepare_search_url(query, page, region)
        res = await self.__get_response(url)
        return self.__scraper.parse_part_search(res)


    async def get_part_reviews(
        self, id_url: str, page: int = 1, rating: Optional[int] = None
    ) -> Coroutine[None, None, PartReviewsResult]:
        url = self.__scraper.prepare_part_reviews_url(id_url, page, rating)
        res = await self.__get_response(url)
        return self.__scraper.parse_reviews(res)

