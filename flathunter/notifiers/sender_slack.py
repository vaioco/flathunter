"""Functions and classes related to sending Slack messages"""
import json
from typing import Dict

import requests

from flathunter.abstract_notifier import Notifier
from flathunter.abstract_processor import Processor
from flathunter.config import YamlConfig
from flathunter.logging import logger


class SenderSlack(Processor, Notifier):
    """Expose processor that sends Slack messages"""

    def __init__(self, config: YamlConfig) -> None:
        self.config = config
        self.webhook_url = self.config.slack_webhook_url()

    def process_expose(self, expose: Dict) -> Dict:
        """Send a message to a Slack channel describing the expose"""
        message = self.config.message_format().format(
            title=expose['title'],
            rooms=expose['rooms'],
            size=expose['size'],
            price=expose['price'],
            url=expose['url'],
            address=expose['address'],
            durations="" if 'durations' not in expose else expose[
                'durations']).strip()
        self.notify(message)
        return expose

    def notify(self, message: str) -> None:
        """Send message to the Slack webhook"""
        self.__send_message(message)

    def __send_message(self, message: str) -> None:
        """Send messages to the Slack webhook"""
        logger.debug(('webhook_url:', self.webhook_url))
        logger.debug(('message', message))
        response = requests.post(
            self.webhook_url,
            data=json.dumps({"text": message}),
            timeout=30
        )
        logger.debug("Got response (%i): %s", response.status_code, response.content)

        if response.status_code != 200:
            logger.error(
                "When sending Slack bot message, we got status %i with message: %s",
                response.status_code,
                response.text
            )
