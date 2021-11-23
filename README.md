# combined-shop-scraper
A simple, configurable and expandable combined shop scraper to minimize the costs of ordering several items.
## Features
- Define an input file components.json with components to be scraped and the source urls
- Find the cheapest order combination including the shipping prices
- Get alarm prices when single components are below a defined price
- Easily expand for new shops (scraping basic know-how required). Default basic support for:
  - PC component shops: [notebooksbilliger](https://www.notebooksbilliger.de/), [cyberport](https://www.cyberport.de/) and [future-x](https://www.future-x.de/)
  - Bike shops: [bike-components](https://www.bike-components.de) and [bike-discount](https://www.bike-discount.de)
## Usage
### JSON file definition
The default name of the input JSON file is [`components.json`](scraper/components.json) (which can be also passed as optional positional argument) and must be located in the same folder as [`scraper.py`](scraper/scraper.py). This is the basic structure of the file:
```json
{
  "component1": {
    "alarm_price": 260,
    "quantity": 1,
    "urls": [
      "https://www.someshop.com/component1",
      "https://www.someshop.com/component1-alternative",
      "https://www.anothershop.com/component1-alternative"]
  },
  "component2": {
    "urls": [
      "https://www.someshop.com/component2",
      "https://www.anothershop.com/component2",
      "https://www.onemoreshop.com/component2"]
  }
```
The component name and at least one url are mandatory. It is possible to add several urls from the same shop for the same component if there are some alternatives for this. The quantity of each component defaults to 1, the alarm price is optional.
### Execution
Just call the script [`scraper.py`](scraper/scraper.py) from within the folder, so the [`components.json`](scraper/components.json) file can be found. You can also pass the input file as parameter, like this:
```sh
python3 scraper.py input_file.json
```

It will print an overview of the ideal order to minimize the overall cost. The program runs just once and does not keep tracking prices in the background. As usual with scraping, be gentle and fair and don't abuse this program. 
### Addition of new shops
If you want to add a new shop, you need to edit the file [`shops.py`](scraper/shops.py) and:
- Enter the significant part of the shop url in the method `Shop._get_shops_dict` and define a new class type (child of `Shop`)
- Implement the methods `_process_soup` and `get_shipping_cost` for the new class. Use the existing classes as reference for the data you need to scrap.
- Add your new urls to the input file!
## License
Copyright (c) 2021 javiser
`combined-shop-scraper` is distributed under the terms of the MIT License.

See the [LICENSE](LICENSE) for license details.
