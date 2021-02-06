import re


def get_list_links(string):
    list_regex = re.compile("((?:http|https)://(?:[a-z]{2}.pcpartpicker|pcpartpicker).com/list/(?:[a-zA-Z0-9]{6}))")
    return re.findall(list_regex, string)


def get_product_links(string):
    product_regex = re.compile("((?:http|https)://(?:[a-z]{2}.pcpartpicker|pcpartpicker).com/product/(?:[a-zA-Z0-9]{6}))")
    return re.findall(product_regex, string)
