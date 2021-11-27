import requests
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List


@dataclass
class Product:
    name: str = ""
    price: float = 0
    shop: str = ""

    def __str__(self):
        if self.name:
            return f"{self.name}: {self.price:.2f}€ (@{self.shop})"
        return "No valid product"


class Shop(ABC):
    def __str__(self):
        shops_dict = self._get_shops_dict()
        return next(
            (shop for shop in shops_dict if type(shops_dict[shop]) is type(self))
        )

    @classmethod
    def _get_shops_dict(self) -> dict:
        return {
            "notebooksbilliger": NotebooksBilligerShop(),
            "cyberport": CyberPortShop(),
            "future-x": FutureXShop(),
            "bike-components": BikeComponentsShop(),
            "bike-discount": BikeDiscountShop(),
        }

    @classmethod
    def get_shops_list(self) -> List[str]:
        return list(self._get_shops_dict())

    @classmethod
    def get_product_from_url(self, url: str) -> Product:
        shops_dict = self._get_shops_dict()
        try:
            shop_name = next((shop for shop in shops_dict if shop in url))
        except StopIteration:
            # Shop not found
            return None
        shop = shops_dict[shop_name]
        return shop.scrape_product(url)

    def scrape_product(self, url: str) -> Product:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
        }

        website = requests.get(url, headers=headers)
        self.soup = BeautifulSoup(website.content, "html.parser")
        try:
            self._process_soup()
        except requests.exceptions.InvalidURL:
            self.price = None
            self.name = None

        return Product(price=self.price, name=self.name, shop=str(self))

    @classmethod
    def calculate_shipping_price(self, shop: str, total_order: float) -> float:
        shops_dict = self._get_shops_dict()
        if shop in shops_dict:
            return shops_dict[shop].get_shipping_cost(total_order)
        return None

    @abstractmethod
    def _process_soup(self):
        """This method is shop-specific and processes the soup to get the price and product name"""

    @abstractmethod
    def get_shipping_cost(self, total_order: float) -> float:
        """This method is shop-specific and returns the shipping cost based on the total order amount for that shop"""


class NotebooksBilligerShop(Shop):
    def _process_soup(self):
        self.name = (
            self.soup.find("title").get_text().replace(" bei notebooksbilliger.de", "")
        )
        product_price_container = self.soup.find_all(
            lambda tag: tag.name == "div"
            and tag.get("class") == ["product-price__container"]
        )
        if not product_price_container:
            raise requests.exceptions.InvalidURL
        price_part = product_price_container[0].find_all(
            "span", class_="product-price__regular js-product-price"
        )
        self.price = float(price_part[0].get_text().split()[0].replace(",", "."))

    def get_shipping_cost(self, total_order: float) -> float:
        if total_order < 250:
            return 3.99
        else:
            return 7.99


class CyberPortShop(Shop):
    def _process_soup(self):
        self.name = self.soup.find("title").get_text().replace(" ++ Cyberport", "")
        product_price_container = self.soup.find_all("span", class_="online-price")
        if not product_price_container:
            raise requests.exceptions.InvalidURL
        self.price = float(
            product_price_container[0].get_text().split()[1].replace(",", ".")
        )

    def get_shipping_cost(self, total_order: float) -> float:
        if total_order < 200:
            return 4.99
        else:
            return 5.99


class FutureXShop(Shop):
    def _process_soup(self):
        self.name = self.soup.find("title").get_text()
        product_price_container = self.soup.find("span", class_="price")
        if not product_price_container:
            raise requests.exceptions.InvalidURL
        self.price = float(
            product_price_container.get_text().split()[0].replace(",", ".")
        )

    def get_shipping_cost(self, total_order: float) -> float:
        return 0


class BikeComponentsShop(Shop):
    def _process_soup(self):
        self.name = self.soup.find("title").get_text().replace(" - bike-components", "")
        product_price_container = self.soup.find("div", class_="stock-price")
        if not product_price_container:
            raise requests.exceptions.InvalidURL
        self.price = float(
            product_price_container.get_text()
            .split()[0]
            .replace(",", ".")
            .replace("€", "")
        )

    def get_shipping_cost(self, total_order: float) -> float:
        return 3.95


class BikeDiscountShop(Shop):
    def _process_soup(self):
        self.name = (
            self.soup.find("title")
            .get_text()
            .replace(" kaufen | Bike-Discount", "")
            .splitlines()[0]
        )
        product_price_container = self.soup.find(
            "span", class_="price--content content--default"
        )
        if not product_price_container:
            raise requests.exceptions.InvalidURL
        self.price = float(
            product_price_container.get_text().split()[1].replace(",", ".")
        )

    def get_shipping_cost(self, total_order: float) -> float:
        if total_order < 99:
            return 3.99
        else:
            return 0
