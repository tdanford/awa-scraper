import requests
import re
import time

from tqdm import tqdm
from urllib.parse import urljoin
from bs4 import BeautifulSoup as BS
from lxml import etree

from awa.cached import Cached
from awa.crawler import CrawlingQueue


class DataSourceError(Exception):
    def __init__(self, source, url, status_code):
        Exception.__init__(self)
        self.source = source
        self.url = url
        self.status_code = status_code


class DataSource(Cached):
    def __init__(self, name, url):
        Cached.__init__(self, url)
        self.name = name

    def find_links(self):
        return []


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
        urls = [self.url] + [self.relative_url(link.get("href")) for link in other_parts]
        cacheable = [Cached(u) for u in urls]

        with tqdm(total=len(urls), position=0) as pbar:
            for gettable in cacheable:
                soup = gettable.soup()
                links = [
                    x
                    for x in soup.find_all("a")
                    if x.get("href") is not None and "itemlink" in x.get_attribute_list("class")
                ]
                for link in links:
                    title = link.text.strip().replace("\n", "")
                    href = gettable.relative_url(link.get("href"))
                    yield title, href
                pbar.update(1)


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
                links = [x for x in cached.soup().find_all("a") if x.get("href").endswith("pdf")]
                for link in links:
                    title = link.get("href").split("/")[-1]
                    link = cached.relative_url(link.get("href"))
                    yield title, link
                pbar.update(1)


class SigarReports(DataSource):
    def __init__(self):
        DataSource.__init__(
            self, "SIGAR Reports", "https://www.sigar.mil/allreports/index.aspx?SSR=5"
        )
        self.sigar_xml_urls = [
            "https://www.sigar.mil/Newsroom/spotlight/spotlight.xml",
            "https://www.sigar.mil/Newsroom/pressreleases/press-releases.xml",
            "https://www.sigar.mil/Newsroom/testimony/testimony.xml",
            "https://www.sigar.mil/Newsroom/speeches/speeches.xml",
            "https://www.sigar.mil/audits/auditreports/reports.xml",
            "https://www.sigar.mil/audits/evaluationreports/evaluation-reports.xml",
            "https://www.sigar.mil/audits/inspectionreports/inspection-reports.xml",
            "https://www.sigar.mil/audits/financialreports/Financial-Audits.xml",
            "https://www.sigar.mil/SpecialProjects/reviews/reviews.xml",
            "https://www.sigar.mil/SpecialProjects/factsheets/fact-sheets.xml",
            "https://www.sigar.mil/SpecialProjects/mgmtandalertletters/mgmt-alert-letters.xml",
            "https://www.sigar.mil/SpecialProjects/inquiryletters/inquiry-letters.xml",
            "https://www.sigar.mil/SpecialProjects/otherpublications/other-publications.xml",
            "https://www.sigar.mil/investigations/alert-special-reports.xml",
            "https://www.sigar.mil/Audits/alertandspecialreports/alert-special-reports.xml",
            "https://www.sigar.mil/quarterlyreports/index.xml",
            "https://www.sigar.mil/LessonsLearned/LessonsLearnedReports/lessons-learned-reports.xml",
        ]

    def find_links(self):
        queue = CrawlingQueue([Cached(u, ignore_errors=True) for u in self.sigar_xml_urls], bar_position=0)
        for cached, xml_string in queue.crawl(): 
            try:
                root = etree.fromstring(xml_string.encode("UTF-8"))
                for item in root.findall("*/item"):
                    title = item.find("title").text
                    relative_link = item.find("link").text.replace("\n", "").strip()
                    full_link = cached.relative_url(relative_link)
                    yield title, full_link
            except etree.XMLSyntaxError as err:
                pass
            except AttributeError as err: 
                pass 


class AREUReports(DataSource):
    def __init__(self):
        DataSource.__init__(self, "AREU Reports", "https://areu.org.af/publications/")
        self.search_url = "https://areu.org.af/publications/?keyword=afghanistan"

    def find_links(self):
        soup = Cached(self.search_url).soup()
        links = [x for x in soup.find_all("a") if x.get("download") is not None]
        for link in links:
            yield link.get("download"), link.get("href")
