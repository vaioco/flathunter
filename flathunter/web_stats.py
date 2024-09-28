from flathunter.logging import logger
from datetime import time
from datetime import datetime as dt, timedelta
from flathunter.time_utils import is_current_time_between, get_time_span_in_secs, wait_during_period
from flathunter.logging import logger


class WebStats:
    def __init__(self, config , name : str) -> None:
        self.requests_counter :int  = int()
        self.max_request : int = int()
        self.last_request_time : dt = dt.min
        self.parking_time : int = 86400 # 1 day in secs
        self.crawler_name : str = str()
        self.config = config
        self.name = name
        self.end_time = dt.now()

    def isGreenLight(self) -> bool:
        if self.last_request_time == dt.min:
            self.last_request_time = dt.now()
            return True
        return False

    def parking(self):
        sleep_for = timedelta(seconds=self.parking_time)
        self.end_time = self.last_request_time + sleep_for
        logger.info("going to sleep for %d seconds - wakeup: %s", sleep_for, self.end_time.time())
        wait_during_period(self.last_request_time.time(),self.end_time.time())
        logger.info("woke up at: %s", dt.now().time())


    def addRequest(self):
        self.requests_counter += 1
        self.last_request_time = dt.now()
        self.print_stat()

    def print_stat(self):
        logger.info("STATS: #request %d - last req time: %s - end time: %s", self.requests_counter, self.last_request_time.time(), self.end_time.time())
