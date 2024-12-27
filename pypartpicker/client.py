import asyncio
from .scraper import Scraper
from .types import Part, PartList, PartSearchResult, PartReviewsResult
from .errors import CloudflareException, RateLimitException
from requests import Response
from requests_html import HTMLSession, AsyncHTMLSession
from typing import Coroutine, Optional
import time


class Client:
    def __init__(
        self,
        max_retries=3,
        retry_delay=0,
        response_retriever=None,
        no_js=False,
        cookies=None,
    ):
        self.__scraper = Scraper()
        self.__session = HTMLSession()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cookies = cookies
        self.no_js = no_js

        self.__get_response = (
            response_retriever
            if response_retriever is not None
            else self.__default_response_retriever
        )
        if not callable(self.__get_response):
            raise ValueError("response_retriever must be callable.")

    def __default_response_retriever(self, url: str, retries=0) -> Response:
        if retries >= self.max_retries:
            raise CloudflareException(f"Request to {url} failed, max retries exceeded.")

        res = self.__session.get(url, cookies=self.cookies)

        # Check if we are being Cloudflare checked
        if self.__scraper.is_cloudflare(res):
            if self.no_js:
                return self.__default_response_retriever(url, self.max_retries)

            res.html.render()

            if self.__scraper.is_cloudflare(res):
                time.sleep(self.retry_delay)
                return self.__default_response_retriever(url, retries + 1)
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

    # def get_parts(
    #     self,
    #     product_path: str,
    #     page: int = 1,
    #     region: Optional[str] = None,
    #     compatible_with: Optional[str] = None,
    # ) -> PartSearchResult:
    #     url = self.__scraper.prepare_parts_url(
    #         product_path, page, region, compatible_with
    #     )
    #     res = self.__get_response(url)
    #     res.html.render()
    #     return self.__scraper.parse_parts(res)


class AsyncClient:
    def __init__(
        self,
        max_retries=3,
        retry_delay=0,
        response_retriever=None,
        cookies=None,
        no_js=False,
    ):
        self.__scraper = Scraper()
        self.__session = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cookies = cookies
        self.no_js = no_js

        self.__get_response = (
            response_retriever
            if response_retriever is not None
            else self.__default_response_retriever
        )
        if not callable(self.__get_response):
            raise ValueError("response_retriever must be callable.")

    async def __aenter__(self):
        self.__session = AsyncHTMLSession()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__session.close()

    async def __default_response_retriever(
        self, url: str, retries=0
    ) -> Coroutine[None, None, Response]:
        if retries >= self.max_retries:
            raise CloudflareException(f"Request to {url} failed, max retries exceeded.")

        res = await self.__session.get(url, cookies=self.cookies)

        # Check if we are being Cloudflare checked
        if self.__scraper.is_cloudflare(res):
            if self.no_js:
                return await self.__default_response_retriever(url, self.max_retries)

            await res.html.arender()

            if self.__scraper.is_cloudflare(res):
                asyncio.sleep(self.retry_delay)
                return await self.__default_response_retriever(url, retries + 1)
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
