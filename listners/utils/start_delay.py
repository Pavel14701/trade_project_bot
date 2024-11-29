from datetime import datetime, timedelta
import time

class StartDelayCalc:
    @staticmethod
    def startdelay():
        now = datetime.now()
        midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        delay = (midnight - now).total_seconds()
        time.sleep(delay)