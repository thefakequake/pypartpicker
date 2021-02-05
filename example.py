from pypartpicker.pypartpicker import product_search, fetch_list, fetch_product

product = fetch_product("https://pcpartpicker.com/product/crqBD3/phanteks-eclipse-p300a-mesh-atx-mid-tower-case-ph-ec300atg_bk01")

print(product.rating)



