from awa.sources import *

import pathlib

if __name__ == "__main__":
    path = pathlib.Path.cwd() / "master_links.csv"
    output_master_csv(path)
