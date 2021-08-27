from tqdm import tqdm

from awa.cached import Cached
from awa.data_source import DataSource


class CentcomQuarterlyReports(DataSource):
    def __init__(self):
        DataSource.__init__(
            self,
            "CENTCOM Quarterly Contractor Census Reports",
            "https://www.acq.osd.mil/log/ps/CENTCOM_reports.html",
        )
        self.urls = [
            "https://www.acq.osd.mil/log/ps/CENTCOM_reports.html",
            "https://www.acq.osd.mil/log/PS/archvd_CENTCOM_reports.html",
        ]

    def find_links(self):
        with tqdm(total=len(self.urls), position=0) as pbar:
            for url in self.urls:
                cached = Cached(url)
                links = [
                    x
                    for x in cached.soup().find_all("a")
                    if x.get("href").endswith("pdf")
                ]
                for link in links:
                    title = link.get("href").split("/")[-1]
                    link = cached.relative_url(link.get("href"))
                    yield title, link
                pbar.update(1)
