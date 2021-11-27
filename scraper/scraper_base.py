import coloredlogs
import json
import logging
from typing import List
from scraper.shops import Shop, Product
from scraper.alarm import Alarm


class Scraper:
    def __init__(self):
        coloredlogs.install(level="INFO", fmt="[%(levelname)s] - %(message)s")

    def read_input_file(self, input_file) -> bool:
        try:
            with open(input_file) as file:
                components_database = json.load(file)
        except FileNotFoundError:
            logging.error(f"Could not open input file {input_file}, aborting")
            return False
        except json.decoder.JSONDecodeError:
            logging.error(f"Could not parse input file {input_file}, aborting")
            return False

        self.DB = self._process_urls(components_database)
        if not self.DB:
            logging.error(
                f"The file {input_file} does not contain any valuable data, aborting"
            )
            return False

        return True

    def run(self):
        cheapest_product_combination = self._get_cheapest_product_combination(0)
        print(
            f"\nTotal cost: {self._calculate_total_price(cheapest_product_combination):.2f}€. Chosen combination:"
        )
        for product in cheapest_product_combination:
            print(f"* {product.shop} - {product.name} ({product.price:.2f}€)")

    def _calculate_total_price(self, product_list: List[Product]) -> float:
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

    def _get_cheapest_product_combination(self, comp_index: int) -> List[Product]:
        component = list(self.DB)[comp_index]
        min_price = None

        for shop in self.DB[component]:
            if shop == "quantity":
                continue
            if comp_index + 1 < len(list(self.DB)):
                product_list = self._get_cheapest_product_combination(comp_index + 1)
            else:
                product_list = [Product() for comp in list(self.DB)]
            product_name = list(self.DB[component][shop])[0]
            product_price = self.DB[component][shop][product_name]
            product_quantity = self.DB[component]["quantity"]
            product_list[comp_index].price = product_price * product_quantity
            product_list[comp_index].name = product_name
            product_list[comp_index].shop = shop
            total_price = self._calculate_total_price(product_list)
            if not min_price or total_price < min_price:
                min_price = total_price
                best_product_list = product_list

        return best_product_list

    def _process_urls(self, url_DB: dict) -> dict:
        output_DB = {}
        for component in url_DB:
            logging.info(f"* {component}:")
            url_DB[component]["shops"] = {}

            if "urls" not in url_DB[component]:
                logging.error(
                    f"No urls defined for component {component}, skipping this"
                )
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
                    alarm = Alarm(product, alarm_price)
                    alarm.trigger()
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
