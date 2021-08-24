"""Utilities for dealing with mater-link.csv
"""

import csv
import pathlib
import os
import logging

master_links_filename = os.getenv("MASTER_LINKS", "links/master-links.csv")


class MasterLink:
    def __init__(self, source_name, source_url, title, url):
        self.source_name = source_name
        self.source_url = source_url
        self.title = title
        self.url = url

    def __repr__(self):
        return f"{self.title} ({self.source_name}) {self.url}"

    def row(self):
        return [self.source_name, self.source_url, self.title, self.url]


class MasterLinkFile:
    def __init__(self, filename=master_links_filename):
        self.path = pathlib.Path(filename)

    def write_links(self, links):
        with self.path.open("wt") as outf:
            writer = csv.writer(outf)
            writer.writerow(["Source Name", "Source URL", "Name", "URL"])
            for link in links:
                if not isinstance(link, MasterLink):
                    logging.error(
                        f"Cannot write {link} to master-links.csv since the item is not a MasterLink object"
                    )
                else:
                    writer.writerow(link.row())

    def append_link(self, link):
        with self.path.open("a") as outf:
            writer = csv.writer(outf)
            writer.writerow(link.row())

    def read_links(self):
        with self.path.open("rt") as inf:
            reader = csv.reader(inf)
            header = next(reader)
            return [MasterLink(*row) for row in reader]
