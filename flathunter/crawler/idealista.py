"""Expose crawler for Idealista"""
import re
import requests
import json
from flathunter.logging import logger
from flathunter.abstract_crawler import Crawler

class CrawIdealistaAPI(Crawler):

    APIv3URL = 'https://api.idealista.com/3.5/es/search'
    URL_PATTERN = re.compile(r'https://api\.idealista\.com')
    KEYS = ['propertyCode', 'thumbnail', 'url', 'title', 'price', 'size', 'rooms','district']
    def __init__(self, config):
        super().__init__(config)
        self.config = config
    
    def get_page(self, search_url, driver=None, page_no=None):
        post_data = {
            'center': (None,'41.3874,2.1686'),
            'propertyType':(None,'homes'),
            'distance':(None,'15000'),
            'locale':(None,'en'),
            'operation':(None,'rent'),
            'maxItems': (None,'50'),
            'minSize': (None, '40'),
            'flat': (None, True),
            'maxPrice': (None, '2000'),
            'order' : (None, 'publicationDate'),
            'sort' : (None, 'desc'),
            'furnished' : (None, 'furnished'),
            # 'bankOffer' : (None, True),
            'elevator' : (None, True),
        }

        ## TODO this is a tmp token
        MYHEADERS = {
        'Authorization': 'Bearer' + self.config.idealista_auth() ,        
        }

        resp = requests.post(search_url, files=post_data, headers=MYHEADERS, timeout=30)
        if resp.status_code not in (200, 405):
            user_agent = 'Unknown'
            if 'User-Agent' in self.HEADERS:
                user_agent = self.HEADERS['User-Agent']
            logger.error("Got response (%i): %s\n%s",
                         resp.status_code, resp.content, user_agent)
        logger.debug('got resp status %d', resp.status_code)
        return resp.json()   

    def extract_data(self, jdata):
        entries = []
        for elem in jdata['elementList']:
            logger.debug(elem)
            details = {
                'id': int(elem['propertyCode']),
                'image': elem['thumbnail'],
                'url': elem['url'],
                'title': elem['description'][:500],
                'price': str(elem['price']),
                'size': str(elem['size']),
                'rooms': str(elem['rooms']),
                'address': elem['address'],
                'lift': str(elem['hasLift']),
                'pricebyarea': str(elem['priceByArea']),
                'neighborhood': str(elem['neighborhood']),
                'district': str(elem['district']),
                'bathrooms': str(elem['bathrooms']),
                'status': elem['status'],
                'lat' : str(elem['latitude']),
                'long' : str(elem['longitude']),
                'crawler': self.get_name()
            }
            entries.append(details)            
        logger.debug('total: %d', jdata['total'])
        logger.debug('processed %d', len(entries))
        return entries


class CrawlIdealista(Crawler):
    """Implementation of Crawler interface for Idealista"""

    URL_PATTERN = re.compile(r'https://www\.idealista\.it')

    def __init__(self, config):
        super().__init__(config)
        self.config = config

    # pylint: disable=unused-argument
    def get_page(self, search_url, driver=None, page_no=None):
        """Applies a page number to a formatted search URL and fetches the exposes at that page"""
        if self.config.use_proxy():
            return self.get_soup_with_proxy(search_url)

        return self.get_soup_from_url(search_url)

    # pylint: disable=too-many-locals
    def extract_data(self, soup):
        """Extracts all exposes from a provided Soup object"""
        entries = []

        findings = soup.find_all('article', {"class": "item"})

        base_url = 'https://www.idealista.it'
        for row in findings:
            title_row = row.find('a', {"class": "item-link"})
            title = title_row.text.strip()
            url = base_url + title_row['href']
            picture_element = row.find('picture', {"class": "item-multimedia"})
            if "no-pictures" not in picture_element.get("class"):
                image = ""
            else:
                print(picture_element)
                image = picture_element.find('img')['src']

            # It's possible that not all three fields are present
            detail_items = row.find_all("span", {"class": "item-detail"})
            rooms = detail_items[0].text.strip() if (len(detail_items) >= 1) else ""
            size = detail_items[1].text.strip() if (len(detail_items) >= 2) else ""
            floor = detail_items[2].text.strip() if (len(detail_items) >= 3) else ""
            price = row.find("span", {"class": "item-price"}).text.strip().split("/")[0]

            details_title = (f"{title} - {floor}") if (len(floor) > 0) else title

            details = {
                'id': int(row.get("data-adid")),
                'image': image,
                'url': url,
                'title': details_title,
                'price': price,
                'size': size,
                'rooms': rooms,
                'address': re.findall(r'(?:\sin\s|\sa\s)(.*)$', title)[0],
                'crawler': self.get_name()
            }

            entries.append(details)

        logger.debug('Number of entries found: %d', len(entries))

        return entries
