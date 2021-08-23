import itertools 
import requests 
from awa.sources.data_source import DataSource
from awa.crawler import CrawlingQueue

from bs4 import BeautifulSoup as BSoup

class WhiteHouseReleases(DataSource): 
	def __init__(self): 
		DataSource.__init__(
			self, 
			"White House Releases", 
			"https://www.whitehouse.gov/briefing-room/speeches-remarks/"
		)
	def find_links(self): 
		all_pages = [RemarksPage(i+1) for i in range(27)] 
		crawler = CrawlingQueue(all_pages, follow_links=False)
		for remarks_page in crawler.crawl(): 
			for link in remarks_page.links: 
				yield link 

class RemarksPage:
    def __init__(self, index):
        self.index = index
        self.url = f"https://www.whitehouse.gov/briefing-room/speeches-remarks/page/{index}/"

    def retrieve(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            raise ValueError(f"Couldn't crawl {self.url}")
        self.raw_html = response.text
        self.soup = BSoup(self.raw_html, "html.parser")
        self.links = [
            x
            for x in self.soup.find_all("a")
            if x.get("href") is not None and "news-item__title" in x.get_attribute_list("class")
        ]
        self.remarks = [Remarks(link.get_text(), link.get("href")) for link in self.links]
        return self.remarks


class Remarks:
    def __init__(self, title, url):
        self.title = title.replace("\n", "").replace("\t", "")
        self.url = url

    def retrieve(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            raise ValueError(f"Couldn't crawl {self.url}")
        self.raw_html = response.text
        self.soup = BSoup(self.raw_html, "html.parser")
        sections = self.soup.find_all("section")
        body_sections = [x for x in sections if "body-content" in x.get_attribute_list("class")]
        if len(body_sections) == 0:
            raise ValueError("Can't find body-content section in {self.url}")
        self.text = body_sections[0].get_text()
        return []

