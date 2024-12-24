import re
from .urls import *

PCPP_BASE_RE = re.compile("(http|https)://([a-zA-Z]{2}\.)?pcpartpicker\.com")
ID_RE = re.compile("(\w{6})")
PRODUCT_URL_RE = re.compile(PCPP_BASE_RE.pattern + BASE_PRODUCT_PATH + ID_RE.pattern)
PRODUCT_RATINGS_RE = re.compile("\(([0-9]+) Ratings?, ([0-9]\.[0-9]) Average\)")
DECIMAL_RE = re.compile("[0-9]+\.[0-9]+")
PART_LIST_URL_RE = re.compile(
    PCPP_BASE_RE.pattern + BASE_PART_LIST_PATH + ID_RE.pattern
)
