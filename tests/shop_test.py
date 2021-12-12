import pytest
from scraper.shops import ProductException, Shop


def test_shops_list_not_empty():
    assert len(Shop.get_shops_list()) > 0


def test_shops_scrape_from_non_existing_shop():
    with pytest.raises(ProductException):
        product = Shop.get_product_from_url("https://www.some-dummy-address.com")


def test_shops_scrape_from_invalid_address():
    with pytest.raises(ProductException):
        product = Shop.get_product_from_url("https://www.notebooksbilliger.de")
