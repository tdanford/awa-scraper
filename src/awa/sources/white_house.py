import itertools
import requests

from tqdm import tqdm
from bs4 import BeautifulSoup as BSoup

from awa.sources.data_source import DataSource
from awa.crawler import CrawlingQueue
from awa.cached import Cached


class WhiteHouseReleases(DataSource):
    """A DataSource for retrieving all the links to White House Remarks and Speeches"""

    def __init__(self):
        DataSource.__init__(
            self,
            "White House Releases",
            "https://www.whitehouse.gov/briefing-room/speeches-remarks/",
        )

    def find_links(self):
        count = 27  # dumb, hard-coded.
        all_pages = [RemarksIndexPage(i + 1) for i in range(count)]
        crawler = CrawlingQueue(all_pages, retriever=lambda v: v.retrieve())
        for index_page, remarks_page in crawler.crawl():
            for link in remarks_page.links:
                yield link.text, link.get("href")


class RemarksIndexPage(Cached):
    """Class for finding the links to the remarks themselves (and using the text of the anchor
    link as the title of the remarks)
    """

    def __init__(self, index):
        Cached.__init__(
            self,
            f"https://www.whitehouse.gov/briefing-room/speeches-remarks/page/{index}/",
        )

    def retrieve(self):
        parsed = self.soup()
        self.links = [
            x
            for x in parsed.find_all("a")
            if x.get("href") is not None
            and "news-item__title" in x.get_attribute_list("class")
        ]
        self.remarks = [
            Remarks(link.get_text(), link.get("href")) for link in self.links
        ]
        return self


class Remarks(Cached):
    """Class for actually scraping the contents of each remark"""

    def __init__(self, title, url):
        Cached.__init__(self, url)
        self.title = title.replace("\n", "").replace("\t", "")

    def retrieve(self):
        parsed = self.soup()
        sections = parsed.find_all("section")
        body_sections = [
            x for x in sections if "body-content" in x.get_attribute_list("class")
        ]
        if len(body_sections) == 0:
            raise ValueError("Can't find body-content section in {self.url}")
        self.text = body_sections[0].get_text()
        return self
