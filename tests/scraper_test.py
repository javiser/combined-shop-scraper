from pathlib import Path
from scraper.scraper_base import Scraper


def test_scraper_no_input_file():
    scraper = Scraper()
    assert scraper.read_input_file("") == False


def test_scraper_not_existing_input_file():
    scraper = Scraper()
    assert scraper.read_input_file("not_existing_file") == False


def test_scraper_read_default_input_file():
    # This takes a while as it performs some parsing
    scraper = Scraper()
    path = Path("data", "components.json")
    assert scraper.read_input_file(path) == True


def test_scraper_read_empty_input_file():
    scraper = Scraper()
    path = Path("tests", "testdata", "empty_file.json")
    assert scraper.read_input_file(path) == False


def test_scraper_read_no_json_input_file():
    scraper = Scraper()
    path = Path("tests", "testdata", "no_json_file.json")
    assert scraper.read_input_file(path) == False


def test_scraper_read_broken_json_input_file():
    scraper = Scraper()
    path = Path("tests", "testdata", "broken_json_file.json")
    assert scraper.read_input_file(path) == False


def test_scraper_read_useless_input_file():
    scraper = Scraper()
    path = Path("tests", "testdata", "useless_input_file.json")
    assert scraper.read_input_file(path) == False


def test_scraper_read_quantity():
    scraper = Scraper()
    path = Path("tests", "testdata", "basic_input_file.json")
    scraper.read_input_file(path)
    assert scraper.DB["CPU"]["quantity"] == 2


def test_scraper_default_quantity_1():
    scraper = Scraper()
    path = Path("tests", "testdata", "minimal_input_file.json")
    scraper.read_input_file(path)
    assert scraper.DB["CPU"]["quantity"] == 1


def test_scraper_wrong_quantity_string():
    scraper = Scraper()
    path = Path("tests", "testdata", "wrong_quantity_string.json")
    scraper.read_input_file(path)
    assert scraper.DB["CPU"]["quantity"] == 1


def test_scraper_wrong_price_alarm_string():
    scraper = Scraper()
    path = Path("tests", "testdata", "wrong_alarm_price_string.json")
    scraper.read_input_file(path)
    assert "alarm_price" not in scraper.DB["CPU"]
