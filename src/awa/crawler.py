"""A queue for crawling pages with a time delay 
"""
import requests
import time

class CrawlingQueue:
    def __init__(self, retrievables, follow_links=True, delay=0.5):
        self.retrievables = retrievables
        self.retrieved = []
        self.follow_links = follow_links
        self.delay = delay 

    def crawl(self):
        while len(self.retrievables) > 0:
            time.sleep(self.delay)
            r = self.retrievables.pop()
            next = r.retrieve()
            self.retrieved.append(r)
            if self.follow_links: 
                self.retrievables.extend(next)
            yield r 


class CrawlerError(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.message = msg

