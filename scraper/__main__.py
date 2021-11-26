import argparse
from pathlib import Path
from scraper.scraper_base import Scraper


def main() -> None:
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

    parser = argparse.ArgumentParser(
        description="Calculate best product-shop combination for a certain list of components defined in a JSON input file"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default=Path("data", "components.json"),
        help="JSON input file",
    )
    input_args = parser.parse_args()

    scraper = Scraper()
    if scraper.read_input_file(input_args.input_file):
        scraper.run()


if __name__ == "__main__":
    main()
