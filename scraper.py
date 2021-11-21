import coloredlogs
import json
import logging
from typing import List

import shops


def calculate_order_price(product_list: List[shops.Product]) -> float:
    total_price = 0
    shops_dict = {shop: 0 for shop in shops.Shop.get_shops_list()}
    for product in product_list:
        if product.shop:
            shops_dict[product.shop] += product.price

    for shop in shops_dict:
        shop_order = shops_dict[shop]
        if not shop_order:
            continue
        shipping_cost = shops.Shop.calculate_shipping_price(shop, shop_order)
        total_price += shop_order + shipping_cost

    return total_price


def get_best_order(DB: dict, comp_index: int) -> List[shops.Product]:
    component = list(DB)[comp_index]
    min_price = None
    best_product_list = []

    for shop in DB[component]:
        if shop == "quantity":
            continue
        if comp_index + 1 < len(list(DB)):
            product_list = get_best_order(DB, comp_index + 1)
        else:
            product_list = [
                shops.Product(price=0, name="", shop="") for comp in list(DB)
            ]
        product_name = list(DB[component][shop])[0]
        product_price = DB[component][shop][product_name]
        product_quantity = DB[component]["quantity"]
        product_list[comp_index].price = product_price * product_quantity
        product_list[comp_index].name = product_name
        product_list[comp_index].shop = shop
        total_price = calculate_order_price(product_list)
        if not min_price or total_price < min_price:
            min_price = total_price
            best_product_list = product_list

    return best_product_list


def process_urls(url_database: dict) -> dict:
    output_DB = {}
    for component in url_database:
        logging.info(f"* {component}:")
        url_database[component]["shops"] = {}
        for url in url_database[component]["urls"]:
            product = shops.Shop.get_product_from_url(url)
            logging.debug(product)
            if (
                "alarm_price" in url_database[component]
                and product.price < url_database[component]["alarm_price"]
            ):
                # This is not yet filled with real functionality
                logging.debug(f"Alarm price for {product.name}:{product.price:.2f}€")
            if product.shop not in url_database[component]["shops"]:
                url_database[component]["shops"][product.shop] = {}
            url_database[component]["shops"][product.shop][product.name] = product.price

        # Now we create the output: a new dictionary which contains only the cheapest product of each shop and the required quantity
        output_DB[component] = {}
        if "quantity" in url_database[component]:
            output_DB[component]["quantity"] = url_database[component]["quantity"]
        else:
            output_DB[component]["quantity"] = 1

        for shop in url_database[component]["shops"]:
            # We add shops only when a product was defined for it
            output_DB[component][shop] = {}
            cheapest = min(
                url_database[component]["shops"][shop],
                key=url_database[component]["shops"][shop].get,
            )
            output_DB[component][shop][cheapest] = url_database[component]["shops"][
                shop
            ][cheapest]
            price = output_DB[component][shop][cheapest]
            logging.info(f"  - @{shop}: {cheapest} -> {price:.2f}€")

    return output_DB


if __name__ == "__main__":
    coloredlogs.install(level="INFO", fmt="[%(levelname)s] - %(message)s")

    with open("components.json") as file:
        components_database = json.load(file)

    DB = process_urls(components_database)
    best_order = get_best_order(DB, 0)
    print(f"\nTotal cost: {calculate_order_price(best_order):.2f}€. Order details:")
    for product in best_order:
        print(f"* {product.shop} - {product.name} ({product.price:.2f}€)")
