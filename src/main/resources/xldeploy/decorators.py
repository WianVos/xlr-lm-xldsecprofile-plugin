import functools, logging, datetime

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class log_with(object):
    """
    Logging decorator that allows you to log with a
    specific logger.
    """
    # Customize these messages
    ENTRY_MESSAGE = 'Entering {}'
    EXIT_MESSAGE = 'Exiting {}'

    def __init__(self, logger=None):
        self.logger = logger

    def __call__(self, func):
        """
         Returns a wrapper that wraps func.\n"
         The wrapper will log the entry and exit points of the function\n"
         with logging.INFO level.\n"
        :param func:
        :return:
        """

        # set logger if it was not set earlier
        if not self.logger:
            logging.basicConfig()
            self.logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args, **kwds):
            self.logger.debug(
                self.ENTRY_MESSAGE.format(func.__name__))  # logging level .info(). Set to .debug() if you want to
            f_result = func(*args, **kwds)
            self.logger.debug(
                self.EXIT_MESSAGE.format(func.__name__))  # logging level .info(). Set to .debug() if you want to
            return f_result

        return wrapper

class timer(object):
    """
    Logging decorator that allows you to log function timings with a
    specific logger.
    """

    def __init__(self, logger=None):
        self.logger = logger

    def __call__(self, func):
        """
         Returns a wrapper that wraps func.\n"
         The wrapper will log the entry and exit points of the function\n"
         with logging.INFO level.\n"
        :param func:
        :return:
        """

        # set logger if it was not set earlier
        if not self.logger:
            logging.basicConfig()
            self.logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args, **kwds):
            st = datetime.datetime.now()
            f_result = func(*args, **kwds)
            et = datetime.datetime.now()
            self.logger.debug("%s duration: %s" % (func.__name__, et - st))
            return f_result

        return wrapper

