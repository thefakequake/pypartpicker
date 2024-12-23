from asyncio import AbstractEventLoop
from .scraper import Scraper
from .part import Part, PartList
from requests import Response
from requests_html import HTMLSession, AsyncHTMLSession
from typing import Coroutine


class Client:
    def __init__(self, **kwargs):
        self.__scraper = Scraper(**kwargs)
        self.__session = HTMLSession()

    def __get_response(self, url: str) -> Response:
        return self.__session.get(url)

    def get_part(self, id_url: str, region: str = None) -> Part:
        url = self.__scraper.prepare_part_url(id_url, region)
        res = self.__get_response(url)
        return self.__scraper.parse_part(res)

    def get_part_list(self, id_url: str, region: str = None) -> PartList:
        url = self.__scraper.prepare_part_list_url(id_url, region)
        res = self.__get_response(url)
        return self.__scraper.parse_part_list(res)


class AsyncClient:
    def __init__(self, **kwargs):
        self.__scraper = Scraper(**kwargs)
        self.__session = None

    async def __aenter__(self):
        self.__session = AsyncHTMLSession()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__session.close()

    async def __get_response(self, url: str) -> Coroutine[None, None, Response]:
        return await self.__session.get(url)

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
