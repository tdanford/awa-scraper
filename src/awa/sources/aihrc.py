import re
from tqdm import tqdm

from awa.data_source import DataSource
from awa.cached import Cached


class AIHRCReports(DataSource):
    def __init__(self):
        DataSource.__init__(
            self,
            "Afghanistan Independent Human Rights Commission",
            "https://www.refworld.org/publisher/AIHRC.html",
        )
        self.segment_link_pattern = re.compile("AIHRC,+\\d+.html")
        self.segment_name_pattern = re.compile("\\d+")

    def is_result_page_link(self, link):
        href = link.get("href")
        link_text = link.text
        return (
            self.segment_link_pattern.search(href) is not None
            and self.segment_name_pattern.search(link_text) is not None
        )

    def find_links(self):
        parsed = self.soup()
        links = [x for x in parsed.find_all("a") if x.get("href") is not None]
        other_parts = [x for x in links if self.is_result_page_link(x)]
        urls = [self.url] + [
            self.relative_url(link.get("href")) for link in other_parts
        ]
        cacheable = [Cached(u) for u in urls]

        with tqdm(total=len(urls), position=0) as pbar:
            for gettable in cacheable:
                soup = gettable.soup()
                links = [
                    x
                    for x in soup.find_all("a")
                    if x.get("href") is not None
                    and "itemlink" in x.get_attribute_list("class")
                ]
                for link in links:
                    title = link.text.strip().replace("\n", "")
                    href = gettable.relative_url(link.get("href"))
                    yield title, href
                pbar.update(1)
