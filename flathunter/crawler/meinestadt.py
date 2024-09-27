"""Expose crawler for MeineStadt"""
import re
import json

from flathunter.logging import logger
from flathunter.webdriver_crawler import WebdriverCrawler

class MeineStadt(WebdriverCrawler):
    """Implementation of Crawler interface for MeineStadt"""

    URL_PATTERN = re.compile(r'https://www\.meinestadt\.de')

    def extract_data(self, soup):
        """Extracts all exposes from a provided Soup object"""
        json_blobs = [ json.loads(node.text)
            for node in soup.find_all("script", { "type": "application/ld+json" }) ]
        entries = sum([ MeineStadt.process_json_list_to_exposes(blob) for blob in json_blobs ], [])
        logger.debug('Number of entries found: %d', len(entries))
        return entries

    @staticmethod
    def process_json_list_to_exposes(json_part):
        """Turn the json blob from the meinstadt page into a list of exposes"""
        return [ expose for blob in json_part
            if (expose := MeineStadt.process_json_blob_to_expose(blob)) is not None ]

    @staticmethod
    def blob_by_graph_type(typename, json_part):
        """Get the @graph type blob with the corresponding type from the json object"""
        subtypes = { item['@type']: item for item in json_part if '@type' in item }
        if typename in subtypes:
            return subtypes[typename]
        return None

    @staticmethod
    def get_number_for_quantitative_value(blob, field):
        """Extract a numeric value from the structured json"""
        if field not in blob:
            return None
        if 'value' not in blob[field]:
            return None
        return blob[field]['value']

    @staticmethod
    def get_address(blob):
        """Extract the object address from the structured json"""
        if 'address' not in blob:
            return None
        if 'name' not in blob['address']:
            return None
        return blob['address']['name']

    @staticmethod
    def get_price(blob):
        """Extract the price from the RealEstateListing"""
        listing = MeineStadt.blob_by_graph_type('RealEstateListing', blob)
        if listing is None:
            print("b")
            return None
        if 'offers' not in listing:
            return None
        if 'priceSpecification' not in listing['offers']:
            return None
        if 'price' not in listing['offers']['priceSpecification']:
            return None
        return listing['offers']['priceSpecification']['price'].replace(".", "")

    @staticmethod
    def process_json_blob_to_expose(blob):
        """Turn a single item from the json into an expose"""
        if '@graph' not in blob:
            return None
        apartment = MeineStadt.blob_by_graph_type('Apartment', blob['@graph'])
        if apartment is None:
            return None
        rooms = MeineStadt.get_number_for_quantitative_value(apartment, 'numberOfRooms')
        size = MeineStadt.get_number_for_quantitative_value(apartment, 'floorSize')
        return {
            'rooms': rooms,
            'size': size,
            'url': apartment['url'],
            'title': apartment['name'],
            'id': int(apartment['url'].split('/')[-1]),
            'image': apartment.get('image', None),
            'crawler': MeineStadt.__name__,
            'address': MeineStadt.get_address(apartment),
            'price': MeineStadt.get_price(blob['@graph'])
        }
