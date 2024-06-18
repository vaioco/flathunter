"""Expose crawler for ImmoWelt"""
import re
import datetime
import hashlib

from bs4 import BeautifulSoup, Tag

from flathunter.logging import logger
from flathunter.abstract_crawler import Crawler

class Immowelt(Crawler):
    """Implementation of Crawler interface for ImmoWelt"""

    URL_PATTERN = re.compile(r'https://www\.immowelt\.de')

    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def get_expose_details(self, expose):
        """Loads additional details for an expose by processing the expose detail URL"""
        soup = self.get_page(expose['url'])
        date = datetime.datetime.now().strftime("%2d.%2m.%Y")
        expose['from'] = date

        immo_div = soup.find("app-estate-object-informations")
        if not isinstance(immo_div, Tag):
            return expose
        immo_div = soup.find("div", {"class": "equipment ng-star-inserted"})
        if not isinstance(immo_div, Tag):
            return expose

        details = immo_div.find_all("p")
        for detail in details:
            if detail.text.strip() == "Bezug":
                date = detail.findNext("p").text.strip()
                no_exact_date_given = re.match(
                    r'.*sofort.*|.*Nach Vereinbarung.*',
                    date,
                    re.MULTILINE|re.DOTALL|re.IGNORECASE
                )
                if no_exact_date_given:
                    date = datetime.datetime.now().strftime("%2d.%2m.%Y")
                break
        expose['from'] = date
        return expose

    # pylint: disable=too-many-locals
    def extract_data(self, soup: BeautifulSoup):
        """Extracts all exposes from a provided Soup object"""
        entries = []
        soup_res = soup.find("main")
        if not isinstance(soup_res, Tag):
            return []

        title_elements = soup_res.find_all("h2")
        expose_ids = soup_res.find_all("a", id=True)

        for idx, title_el in enumerate(title_elements):
            try:
                price = expose_ids[idx].find(
                    "div", attrs={"data-test": "price"}).text
            except IndexError:
                price = ""

            try:
                size = expose_ids[idx].find(
                    "div", attrs={"data-test": "area"}).text
            except IndexError:
                size = ""

            try:
                rooms = expose_ids[idx].find(
                    "div", attrs={"data-test": "rooms"}).text.replace(" Zi.", "")
            except IndexError:
                rooms = ""

            try:
                url = expose_ids[idx].get("href")
            except IndexError:
                continue

            picture = expose_ids[idx].find("picture")
            image = None
            if picture:
                src = picture.find("source")
                if src:
                    image = src.get("data-srcset")

            try:
                address = expose_ids[idx].find(
                    "div", attrs={"class": re.compile("IconFact.*")}
                  )
                address = address.find("span").text
            except (IndexError, AttributeError):
                address = ""

            processed_id = int(
              hashlib.sha256(expose_ids[idx].get("id").encode('utf-8')).hexdigest(), 16
            ) % 10**16

            details = {
                'id': processed_id,
                'image': image,
                'url': url,
                'title': title_el.text.strip(),
                'rooms': rooms,
                'price': price,
                'size': size,
                'address': address,
                'crawler': self.get_name()
            }
            entries.append(details)

        logger.debug('Number of entries found: %d', len(entries))

        return entries
