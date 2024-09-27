"""Providing heartbeat messages"""
from flathunter.abstract_notifier import Notifier
from flathunter.config import YamlConfig
from flathunter.logging import logger
from flathunter.notifiers import SenderApprise, SenderMattermost, SenderTelegram, SenderSlack
from flathunter.exceptions import HeartbeatException


def interval2counter(interval: str) -> int:
    """Transform the string interval to sleeper counter frequencies"""
    if interval is None:
        return 0
    if interval.lower() == 'hour':
        return 3600
    if interval.lower() == 'day':
        return 86400
    if interval.lower() == 'week':
        return 604800
    raise HeartbeatException(
        "No valid heartbeat instruction received - no heartbeat messages will be sent.")


class Heartbeat:
    """Will inform the user on regular intervals whether the bot is still alive"""
    notifier: Notifier
    interval: int

    def __init__(self, config: YamlConfig, interval: str):
        notifiers = config.notifiers()

        if 'mattermost' in notifiers:
            self.notifier = SenderMattermost(config)
        elif 'telegram' in notifiers:
            self.notifier = SenderTelegram(config)
        elif 'apprise' in notifiers:
            self.notifier = SenderApprise(config)
        elif 'slack' in notifiers:
            self.notifier = SenderSlack(config)
        else:
            raise HeartbeatException("No notifier configured - check 'notifiers' config section!")

        self.interval = int(interval2counter(interval)/int(config.loop_period_seconds()))

    def send_heartbeat(self, counter) -> int:
        """Send a new heartbeat message"""
        if not self.notifier or not self.interval:  # interval is disabled
            return counter
        # it's time for a new heartbeat message and reset counter
        if counter % self.interval == 0:
            logger.info('Sending heartbeat message.')
            self.notifier.notify(
                'Beep Boop. This is a heartbeat message. '
                'Your bot is actively searching for flats.'
            )
            counter = 0
        return counter
