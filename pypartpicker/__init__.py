from .types import *
from .client import *
from .urls import *


class Scraper:
    def __init__(self):
        raise Exception(
            "Initialising the library via Scraper is deprecated, use Client or AsyncClient instead.\nRead 2.0 changes here: https://github.com/thefakequake/pypartpicker/tree/2.0"
        )
