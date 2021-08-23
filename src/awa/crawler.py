"""A queue for crawling pages with a time delay 
"""
import requests
import time
from tqdm import tqdm


class CrawlingQueue:
    def __init__(self, retrievables, follow_links=True, delay=0.5):
        self.retrievables = retrievables
        self.retrieved = []
        self.follow_links = follow_links
        self.delay = delay

    def crawl(self):
        with tqdm(total=len(self.retrievables) if not self.follow_links else float("inf"), position=0) as pbar: 
            while len(self.retrievables) > 0:
                time.sleep(self.delay)
                r = self.retrievables.pop()
                next = r.retrieve()
                self.retrieved.append(r)
                if self.follow_links:
                    self.retrievables.extend(next)
                yield r
                pbar.update(1) 


class CrawlerError(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.message = msg
