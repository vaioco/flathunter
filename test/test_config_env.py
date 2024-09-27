import contextlib
import unittest
import tempfile
import os.path
import os
from flathunter.config import Config
from test.utils.config import StringConfig

@contextlib.contextmanager
def modified_environ(*remove, **update):
    """
    Temporarily updates the ``os.environ`` dictionary in-place.

    The ``os.environ`` dictionary is updated in-place so that the modification
    is sure to work in all situations.

    :param remove: Environment variables to remove.
    :param update: Dictionary of environment variables and values to add/update.
    """
    env = os.environ
    update = update or {}
    remove = remove or []

    # List of environment variables being updated or removed.
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    # Environment variables and values to restore on exit.
    update_after = {k: env[k] for k in stomped}
    # Environment variables and values to remove on exit.
    remove_after = frozenset(k for k in update if k not in env)

    try:
        env.update(update)
        [env.pop(k, None) for k in remove]
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]


class EnvConfigTest(unittest.TestCase):

    DUMMY_CONFIG = """
urls:
  - https://www.immowelt.de/

immoscout_cookie: abdcd
"""

    def setUp(self):
         with tempfile.NamedTemporaryFile(mode='w+') as temp:
            temp.write(self.DUMMY_CONFIG)
            temp.flush()
            self.config = Config(temp.name)

    def test_loads_config_from_env(self):
       with modified_environ(FLATHUNTER_DATABASE_LOCATION="test"):
         self.assertEqual("test", os.getenv('FLATHUNTER_DATABASE_LOCATION'))
         self.assertEqual("test", self.config.database_location())

    def test_overrides_url(self):
        self.assertEqual(["https://www.immowelt.de/"], self.config.target_urls())
        with modified_environ(FLATHUNTER_TARGET_URLS="https://fish.com"):
            self.assertEqual(["https://fish.com"], self.config.target_urls())

    def test_is24_cookie(self):
        self.assertEqual("abdcd", self.config.immoscout_cookie())
        with modified_environ(FLATHUNTER_IS24_COOKIE="bbbb"):
            self.assertEqual("bbbb", self.config.immoscout_cookie()) 

