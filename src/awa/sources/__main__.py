import logging
import pathlib

from awa.sources import output_master_csv, configure_logging

if __name__ == "__main__":
    formatter = configure_logging()

    path = pathlib.Path.cwd() / "links" / "master-links.csv"
    output_master_csv(path)
