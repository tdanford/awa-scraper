import time
import logging
import itertools
import requests

from awa.data_source import DataSource
from awa.cached import Cached


class SenateForeignRelationsTranscripts(DataSource):
    def __init__(self, type="Transcript"):
        DataSource.__init__(
            self,
            "Senate Foreign Relations Committee: Transcripts",
            f"https://www.foreign.senate.gov/publications?c=all&type={type}",
        )
        self.type = type

    def find_links(self):
        logging.debug(f"Top: {self.url}")
        top = Cached(self.url)
        page_links = (
            top.soup().find("div", attrs={"style": "display:none"}).find_all("a")
        )
        page_urls = [
            top.relative_url(link.get("href")) + f"&c=all&type={self.type}"
            for link in page_links
        ]
        for page_url in page_urls:
            c = Cached(page_url)
            if not c.is_cached():
                time.sleep(0.25)
            logging.debug(f"Page: {page_url}")
            soup = c.soup()
            rows = [
                x
                for x in soup.find_all("tr")
                if "divider" not in x.get_attribute_list("class")
            ]
            links = [
                (a.text.strip(), c.relative_url(a.get("href")))
                for a in itertools.chain(*[row.find_all("a") for row in rows])
            ]
            for title, link in links:
                result_cache = Cached(link)
                if not result_cache.is_cached():
                    time.sleep(0.25)
                logging.debug(f"Entry: {link}")
                result_soup = result_cache.soup()
                result_anchors = [
                    x
                    for x in result_soup.find_all("a")
                    if x.text.find("click here") != -1
                ]
                if len(result_anchors) > 0:
                    result_link = result_cache.relative_url(
                        result_anchors[0].get("href")
                    )
                    logging.debug(f"Redirected: {result_link}")

                    # if we don't specify a minimally-noticeable User-Agent, then teh server
                    # doesn't respond with a redirect, but instead errors out!
                    response = requests.get(
                        result_link,
                        headers={"User-Agent": "Mozilla/5.0"},
                        allow_redirects=False,
                    )
                    if (
                        int(response.status_code / 100) == 3
                    ):  ## expecting a redirect here
                        location = response.headers.get("Location")
                        logging.debug(f"Location: {location}")
                        result_url = result_cache.relative_url(location)
                        yield title, result_url
                    else:
                        logging.info(f"Didn't get redirect from {result_link}")
