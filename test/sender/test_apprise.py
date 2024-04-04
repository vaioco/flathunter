import json
import unittest
import requests_mock

from test.utils.config import StringConfig
from flathunter.notifiers import SenderApprise


class SenderAppriseTest(unittest.TestCase):

    @requests_mock.Mocker()
    def test_send_no_message_if_no_receivers(self, m):
        config = StringConfig(string=json.dumps({"apprise": []}))
        sender = SenderApprise(config=config)
        self.assertEqual(None, sender.notify("result"), "Expected no message to be sent")