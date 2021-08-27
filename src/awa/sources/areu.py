from awa.data_source import DataSource
from awa.cached import Cached


class AREUReports(DataSource):
    def __init__(self):
        DataSource.__init__(self, "AREU Reports", "https://areu.org.af/publications/")
        self.search_url = "https://areu.org.af/publications/?keyword=afghanistan"

    def find_links(self):
        soup = Cached(self.search_url).soup()
        links = [x for x in soup.find_all("a") if x.get("download") is not None]
        for link in links:
            yield link.get("download"), link.get("href")
