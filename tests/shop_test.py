from scraper.shops import Shop


def test_shops_list_not_empty():
    assert len(Shop.get_shops_list()) > 0


def test_shops_scrape_from_non_existing_shop():
    product = Shop.get_product_from_url("https://www.some-dummy-address.com")
    assert not product


def test_shops_scrape_from_invalid_address():
    product = Shop.get_product_from_url("https://www.notebooksbilliger.de")
    assert not product.name
