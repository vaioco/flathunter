import unittest

import requests_mock

from flathunter.notifiers import SenderApprise


class SenderAppriseTest(unittest.TestCase):

    @requests_mock.Mocker()
    def test_send_no_message_if_no_receivers(self, m):
        sender = SenderApprise({"apprise": [], "apprise_notify_with_images": "false"})
        self.assertEqual(None, sender.notify("result"), "Expected no message to be sent")
