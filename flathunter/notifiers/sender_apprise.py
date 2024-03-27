"""Functions and classes related to sending Apprise messages"""
import apprise

from flathunter.abstract_notifier import Notifier
from flathunter.abstract_processor import Processor


class SenderApprise(Processor, Notifier):
    """Expose processor that sends Apprise messages"""

    def __init__(self, config):
        self.config = config
        self.apprise_urls = self.config.get('apprise', {})

    def process_expose(self, expose):
        """Send a message to a user describing the expose"""
        message = self.config.get('message', "").format(
            crawler=expose.get('crawler', 'N/A'),
            title=expose.get('title', 'N/A'),
            rooms=expose.get('rooms', 'N/A'),
            size=expose.get('size', 'N/A'),
            price=expose.get('price', 'N/A'),
            url=expose.get('url', 'N/A'),
            address=expose.get('address', 'N/A'),
            durations=expose.get('durations', 'N/A')
        ).strip()
        title = self.config.get('title', "").format(
            crawler=expose.get('crawler', 'N/A'),
            title=expose.get('title', 'N/A'),
            rooms=expose.get('rooms', 'N/A'),
            size=expose.get('size', 'N/A'),
            price=expose.get('price', 'N/A'),
            url=expose.get('url', 'N/A'),
            address=expose.get('address', 'N/A'),
            durations=expose.get('durations', 'N/A')
        ).strip()
        self.__send_msg(message, title)
        return expose

    def notify(self, message: str):
        """ Send the given message to users """
        self.__send_msg(message=message, title=None)

    def __send_msg(self, message, title):
        """Send messages to each of the Apprise urls"""
        apobj = apprise.Apprise()
        if self.apprise_urls is None:
            return
        for apprise_url in self.apprise_urls:
            apobj.add(apprise_url)

        apobj.notify(
            body=message,
            title=title,
            body_format=apprise.NotifyFormat.TEXT,
        )
