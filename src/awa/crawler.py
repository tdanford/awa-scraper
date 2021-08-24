"""A queue for crawling pages with a time delay 
"""
import requests
import time
import logging 

from tqdm import tqdm

class CrawlingQueue:
    def __init__(self, retrievables, delay=0.25, bar_position=0, retriever=lambda v: v.get()):
        self.retrievables = retrievables
        self.retrieved = []
        self.delay = delay
        self.bar_position = bar_position
        self.retriever = retriever

    def clear_cached(self):
        for retrievable in self.retrievables:
            retrievable.clear()

    def crawl(self):
        with tqdm(
            total=len(self.retrievables),
            position=self.bar_position,
        ) as pbar:
            while len(self.retrievables) > 0:
                r = self.retrievables.pop()
                if not r.is_cached():
                    time.sleep(self.delay)
                result = self.retriever(r)
                self.retrieved.append(result)
                yield r, result
                pbar.update(1)


class CrawlerError(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.message = msg
