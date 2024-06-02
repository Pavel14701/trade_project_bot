from datetime import datetime, timedelta
import time

class StartDelayCalc:
    """Summary:
    Calculate the start delay until the next midnight.

    Explanation:
    This static method calculates the delay in seconds until the next midnight from the current time using the datetime module and sleeps for that duration.

    Args:
    None

    Returns:
    None
    """


    @staticmethod
    def startdelay():
        """Summary:
        Calculate and apply a start delay until the next midnight.

        Explanation:
        This static method calculates the delay in seconds until the next midnight from the current time using datetime operations and then sleeps for that duration.

        Args:
        None

        Returns:
        None
        """
        now = datetime.now()
        midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        delay = (midnight - now).total_seconds()
        time.sleep(delay)