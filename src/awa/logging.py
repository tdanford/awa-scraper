import logging

LOG_FORMAT = "%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def configure_logging(logging_level=logging.INFO):
    formatter = logging.basicConfig(
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        level=logging_level,
    )
    return formatter
