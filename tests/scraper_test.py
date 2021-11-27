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
    print(path)
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
