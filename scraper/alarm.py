from os import POSIX_FADV_NOREUSE
from scraper.shops import Product


class Alarm:
    def __init__(self, product: Product, alarm_price: float):
        self.product = product
        self.alarm_price = alarm_price

    def trigger(self) -> None:
        # Add your implementation here!
        print(
            f"Alarm for product {self.product} triggered! Price under {self.alarm_price:.2f} €!"
        )
        pass
