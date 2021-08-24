import logging
import pathlib

from awa.sources import output_master_csv

if __name__ == "__main__":
    formatter = logging.basicConfig(
        format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=logging.INFO,
    )

    path = pathlib.Path.cwd() / "links" / "master-links.csv"
    output_master_csv(path)
