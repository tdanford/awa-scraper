"""A queue for crawling pages with a time delay 
"""
import requests
import time
import logging

from tqdm import tqdm


class CrawlerError(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.message = msg


def retrieve(item):
    try:
        return item.get()
    except Exception as err:
        logging.error(str(err))
        return None


class CrawlingQueue:
    def __init__(self, retrievables, delay=0.25, bar_position=0, retriever=retrieve):
        self.retrievables = retrievables
        self.retrieved = []
        self.delay = delay
        self.bar_position = bar_position
        self.retriever = retriever

    def clear_cached(self):
        for retrievable in self.retrievables:
            retrievable.clear()

    def crawl_item(self, item):
        if not item.is_cached():
            time.sleep(self.delay)
        result = self.retriever(item)
        self.retrieved.append(result)
        return (item, result)

    def linear_crawl(self):
        with tqdm(
            total=len(self.retrievables),
            position=self.bar_position,
        ) as pbar:
            while len(self.retrievables) > 0:
                r = self.retrievables.pop()
                try:
                    self.crawl_item(r)
                except CrawlerError as e:
                    logging.error(str(e))
                pbar.update(1)

    def crawl(self):
        with tqdm(
            total=len(self.retrievables),
            position=self.bar_position,
        ) as pbar:
            while len(self.retrievables) > 0:
                r = self.retrievables.pop()
                r, result = self.crawl_item(r)
                yield (r, result)
                pbar.update(1)
