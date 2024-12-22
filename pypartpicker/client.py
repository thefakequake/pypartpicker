from .scraper import Scraper
from .part import Part
from requests import Response
from requests_html import HTMLSession, AsyncHTMLSession

class Client:
    def __init__(self, **kwargs):
        self.__scraper = Scraper(**kwargs)
        self.__session = HTMLSession()
        pass

    def __get_response(self, url: str) -> Response:
        return self.__session.get(url)

    def get_part(self, id_url, **kwargs) -> Part:
        url = self.__scraper.prepare_part_url(id_url, **kwargs)
        res = self.__get_response(url)
        return self.__scraper.parse_part(res)

class AsyncClient:
    def __init__(self, **kwargs):
        self.__scraper = Scraper(**kwargs)
        self.__session = AsyncHTMLSession()
        pass

    async def __get_response(self, url: str) -> Response:
        return await self.__session.get(url)
