import os
import json

import unittest

from flathunter.crawler.meinestadt import MeineStadt
from test.utils.config import StringConfig

class MeineStadtCrawlerTest(unittest.TestCase):

    TEST_URL = 'https://www.meinestadt.de/berlin/immobilien'
    DUMMY_CONFIG = """
    urls:
        - https://www.meinestadt.de/berlin/immobilien
    """

    def setUp(self):
        self.crawler = MeineStadt(StringConfig(string=self.DUMMY_CONFIG))

    def test(self):
        soup = self.crawler.get_page(self.TEST_URL)
        self.assertIsNotNone(soup, "Should get a soup from the URL")
        entries = self.crawler.extract_data(soup)
        self.assertIsNotNone(entries, "Should parse entries from search URL")
        self.assertTrue(len(entries) > 0, "Should have at least one entry")
        self.assertTrue(entries[0]['id'] > 0, "Id should be parsed")
        self.assertTrue(entries[0]['url'].startswith(
            "https://www.meinestadt.de/expose"), u"URL should be an apartment link")
        for attr in ['title', 'price', 'size', 'rooms', 'address', 'image']:
            self.assertIsNotNone(entries[0][attr], attr + " should be set")

    def test_load_expose_from_json(self):
        results = {}
        with open(os.path.join(os.path.dirname(__file__), "fixtures", "meinestadt.json")) as f:
            results = json.load(f)
        exposes = [ x for x in MeineStadt.process_json_list_to_exposes(results) if x is not None ]
        self.assertEqual(20, len(exposes))
