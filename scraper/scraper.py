import argparse
import coloredlogs
import json
import logging
import sys
from typing import List
from shops import Shop, Product


def calculate_total_price(product_list: List[Product]) -> float:
    total_price = 0
    # Contains the sum of the orders for each shop, to calculate shipping price
    shops_dict = {shop: 0 for shop in Shop.get_shops_list()}
    for product in product_list:
        if product.shop:
            shops_dict[product.shop] += product.price

    for shop in shops_dict:
        shop_orders_sum = shops_dict[shop]
        if not shop_orders_sum:
            continue
        shipping_cost = Shop.calculate_shipping_price(shop, shop_orders_sum)
        total_price += shop_orders_sum + shipping_cost

    return total_price


def get_cheapest_product_combination(DB: dict, comp_index: int) -> List[Product]:
    component = list(DB)[comp_index]
    min_price = None

    for shop in DB[component]:
        if shop == "quantity":
            continue
        if comp_index + 1 < len(list(DB)):
            product_list = get_cheapest_product_combination(DB, comp_index + 1)
        else:
            product_list = [Product() for comp in list(DB)]
        product_name = list(DB[component][shop])[0]
        product_price = DB[component][shop][product_name]
        product_quantity = DB[component]["quantity"]
        product_list[comp_index].price = product_price * product_quantity
        product_list[comp_index].name = product_name
        product_list[comp_index].shop = shop
        total_price = calculate_total_price(product_list)
        if not min_price or total_price < min_price:
            min_price = total_price
            best_product_list = product_list

    return best_product_list


def process_urls(url_DB: dict) -> dict:
    output_DB = {}
    for component in url_DB:
        logging.info(f"* {component}:")
        url_DB[component]["shops"] = {}

        if "urls" not in url_DB[component]:
            logging.error(f"No urls defined for component {component}, skipping this")
            continue

        alarm_price = None
        try:
            if "alarm_price" in url_DB[component]:
                alarm_price = float(url_DB[component]["alarm_price"])
        except ValueError:
                logging.error(
                    f"Could not read 'alarm_price' value for component {component}, must be a number. Ignoring alarm price for this component"
                )

        quantity = 1
        try:
            if "quantity" in url_DB[component]:
                quantity = int(url_DB[component]["quantity"])
        except ValueError:
                logging.error(
                    f"Could not read 'quantity' value for component {component}, must be a number. Assuming quantity = 1"
                )

        for url in url_DB[component]["urls"]:
            product = Shop.get_product_from_url(url)
            if not product:
                logging.error(
                    f"The url '{url}' points to an unsupported shop. List of supported shops:"
                )
                for shop in Shop.get_shops_list():
                    logging.error(f" * {shop}")
                continue
            if product.name is None:
                logging.error(f"The url '{url}' seems to be invalid, ignoring it")
                continue
            logging.debug(product)
            if alarm_price and product.price < alarm_price:
                # This is not yet filled with real functionality
                logging.debug(
                    f"Alarm price for {product.name}:{product.price:.2f}€"
                )
            if product.shop not in url_DB[component]["shops"]:
                url_DB[component]["shops"][product.shop] = {}
            url_DB[component]["shops"][product.shop][product.name] = product.price

        # Now we create the output: a new dictionary which contains only the cheapest product of each shop and the required quantity
        output_DB[component] = {}
        output_DB[component]["quantity"] = quantity

        for shop in url_DB[component]["shops"]:
            # We add shops only when a product exists for that shop
            output_DB[component][shop] = {}
            cheapest = min(
                url_DB[component]["shops"][shop],
                key=url_DB[component]["shops"][shop].get,
            )
            output_DB[component][shop][cheapest] = url_DB[component]["shops"][shop][
                cheapest
            ]
            price = output_DB[component][shop][cheapest]
            logging.info(f"  - @{shop}: {cheapest} -> {price:.2f}€")

    return output_DB


if __name__ == "__main__":
    """
    Naming conventions:
        * We want to order "components", in a certain quantity
        * A "url" inside the component relates to a certain "product" from a "shop"
        * Each "product" has a price, a shop and a product name
        * We will choose only "quantity" "products" for each "component"
        * This combination is a "product list" which will result in several "orders"
          for different "shops"
        * Each "order" for a "shop" will have a "shipping price"
        * The sum of all "orders" with their "shipping prices" will be the "total price"
    """
    coloredlogs.install(level="INFO", fmt="[%(levelname)s] - %(message)s")
    parser = argparse.ArgumentParser(
        description="Calculate best product-shop combination for a certain list of components defined in a JSON input file"
    )
    parser.add_argument(
        "input_file", nargs="?", default="components.json", help="JSON input file"
    )
    input_args = parser.parse_args()

    input_file = input_args.input_file
    try:
        with open(input_file) as file:
            components_database = json.load(file)
    except FileNotFoundError:
        logging.error(f"Could not open input file {input_file}, aborting")
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        logging.error(f"Could not parse input file {input_file}, aborting")
        sys.exit(1)

    DB = process_urls(components_database)
    if not DB:
        logging.error(
            f"The file {input_file} does not contain any valuable data, aborting"
        )
        sys.exit(1)
    cheapest_product_combination = get_cheapest_product_combination(DB, 0)
    print(
        f"\nTotal cost: {calculate_total_price(cheapest_product_combination):.2f}€. Chosen combination:"
    )
    for product in cheapest_product_combination:
        print(f"* {product.shop} - {product.name} ({product.price:.2f}€)")
