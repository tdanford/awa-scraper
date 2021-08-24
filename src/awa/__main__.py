import argparse
import logging
import time

if __name__ == "__main__":
    # Always log in UTC and output in RFC3339
    logging.Formatter.converter = time.gmtime

    formatter = logging.basicConfig(
        format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    logging.info("Doing something")
