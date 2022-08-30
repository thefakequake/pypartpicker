import re

LIST_REGEX = re.compile(
    "((?:http|https)://(?:[a-z]{2}.)?pcpartpicker.com/(?:(?:list/(?:[a-zA-Z0-9]{6}))|(?:user/(?:[\\w]+)/saved/(?:[a-zA-Z0-9]{6}))))"
)
PRODUCT_REGEX = re.compile(
    "((?:http|https)://(?:[a-z]{2}.)?pcpartpicker.com/product/(?:[a-zA-Z0-9]{6}))"
)


def get_list_links(string):
    return re.findall(LIST_REGEX, string)


def get_product_links(string):
    return re.findall(PRODUCT_REGEX, string)
