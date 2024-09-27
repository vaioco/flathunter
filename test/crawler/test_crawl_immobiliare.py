import unittest
from flathunter.crawler.immobiliare import Immobiliare
from test.utils.config import StringConfig


class ImmobiliareCrawlerTest(unittest.TestCase):

    TEST_URL = 'https://www.immobiliare.it/affitto-case/milano/?criterio=dataModifica&ordine=desc'
    DUMMY_CONFIG = """
    urls:
      - https://www.immobiliare.it/affitto-case/milano/?criterio=dataModifica&ordine=desc
    """

    def setUp(self):
        self.crawler = Immobiliare(StringConfig(string=self.DUMMY_CONFIG))

    def test(self):
        soup = self.crawler.get_page(self.TEST_URL)
        self.assertIsNotNone(soup, "Should get a soup from the URL")
        entries = self.crawler.extract_data(soup)
        self.assertIsNotNone(entries, "Should parse entries from search URL")
        self.assertTrue(len(entries) > 0, "Should have at least one entry")
        self.assertTrue(entries[0]['id'] > 0, "Id should be parsed")
        self.assertTrue(entries[0]['url'].startswith(
            "https://www.immobiliare.it/annunci/"), u"URL should be an apartment link")
        for attr in ['title', 'price', 'size', 'rooms', 'address', 'image']:
            self.assertIsNotNone(entries[0][attr], attr + " should be set")
