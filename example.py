from pypartpicker import part_search, fetch_product
from time import sleep

parts = part_search("i3", region="uk")

for part in parts:
    if float(part.price.strip("£")) <= 110:
        print(f"I found a valid product: {part.name}")
        print(f"Here is the link: {part.url}")
        product = fetch_product(part.url)
        print(product.specs)
        if product.reviews != None:
            review = product.reviews[0]
            print(f"Posted by {review.author}: {review.content}")
            print(f"They rated this product {review.rating}/5.")
        else:
            print("There are no reviews on this product!")
    sleep(3)