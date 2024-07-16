"""Expose crawler for Kleinanzeigen"""
from typing import Optional

from selenium.webdriver import Chrome
from bs4 import BeautifulSoup

from flathunter.abstract_crawler import Crawler
from flathunter.chrome_wrapper import get_chrome_driver
from flathunter.exceptions import DriverLoadException

class WebdriverCrawler(Crawler):
    """Parent class of crawlers that use webdriver rather than `requests` to fetch pages"""

    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.driver = None

    def get_driver(self) -> Optional[Chrome]:
        """Lazy method to fetch the driver as required at runtime"""
        if self.driver is not None:
            return self.driver
        driver_arguments = self.config.captcha_driver_arguments()
        self.driver = get_chrome_driver(driver_arguments)
        return self.driver

    def get_driver_force(self) -> Chrome:
        """Fetch the driver, and throw an exception if it is not configured or available"""
        res = self.get_driver()
        if res is None:
            raise DriverLoadException("Unable to load chrome driver when expected")
        return res

    def get_page(self, search_url, driver=None, page_no=None) -> BeautifulSoup:
        """Applies a page number to a formatted search URL and fetches the exposes at that page"""
        return self.get_soup_from_url(search_url, driver=self.get_driver())
