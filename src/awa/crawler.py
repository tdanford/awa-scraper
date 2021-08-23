import requests
import time

from bs4 import BeautifulSoup as BSoup


class CrawlingQueue:
    def __init__(self, retrievables):
        self.retrievables = retrievables
        self.retrieved = []
        self.remarks = []

    def crawl(self):
        while len(self.retrievables) > 0:
            time.sleep(0.5)
            r = self.retrievables.pop()
            print(r.url)
            next = r.retrieve()
            self.retrieved.append(r)
            if isinstance(r, Remarks):
                self.remarks.append(r)
            self.retrievables.extend(next)


class CrawlerError(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.message = msg


class RemarksPage:
    def __init__(self, index):
        self.index = index
        self.url = f"https://www.whitehouse.gov/briefing-room/speeches-remarks/page/{index}/"

    def retrieve(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            raise CrawlerError(f"Couldn't crawl {self.url}")
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
            raise CrawlerError(f"Couldn't crawl {self.url}")
        self.raw_html = response.text
        self.soup = BSoup(self.raw_html, "html.parser")
        sections = self.soup.find_all("section")
        body_sections = [x for x in sections if "body-content" in x.get_attribute_list("class")]
        if len(body_sections) == 0:
            raise CrawlerError("Can't find body-content section in {self.url}")
        self.text = body_sections[0].get_text()
        return []


if __name__ == "__main__":
    remarks_page = RemarksPage(1)
    remarks_page.retrieve()
    for link in remarks_page.links:
        print(link)
