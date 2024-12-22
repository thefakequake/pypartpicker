from .scraper import Scraper
from .part import Part, PartList
from requests import Response
from requests_html import HTMLSession, AsyncHTMLSession


class Client:
    def __init__(self, **kwargs):
        self.__scraper = Scraper(**kwargs)
        self.__session = HTMLSession()

    def __get_response(self, url: str) -> Response:
        return self.__session.get(url)

    def get_part(self, id_url, **kwargs) -> Part:
        url = self.__scraper.prepare_part_url(id_url, **kwargs)
        res = self.__get_response(url)
        return self.__scraper.parse_part(res)

    def get_part_list(self, id_url, **kwargs) -> PartList:
        url = self.__scraper.prepare_part_list_url(id_url, **kwargs)
        res = self.__get_response(url)
        return self.__scraper.parse_part_list(res)


class AsyncClient:
    def __init__(self, **kwargs):
        self.__scraper = Scraper(**kwargs)
        self.__session = AsyncHTMLSession()

    async def __get_response(self, url: str) -> Response:
        return await self.__session.get(url)
