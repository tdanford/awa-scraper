import requests
import os
import pathlib
import hashlib
import logging 

from urllib.parse import urljoin
from bs4 import BeautifulSoup as BS
from awa.crawler import CrawlerError

cache_dir = os.getenv("CACHE_DIR", "cache")

class CacheIndex:
    def __init__(self, dir=cache_dir):
        self.dir = pathlib.Path(dir)
        if not self.dir.exists():
            self.dir.mkdir()
        self.index_file = self.dir / "cache_index.txt"
        if not self.index_file.exists():
            self.index_file.touch()
            self.index = []
        else:
            self.load_index()

    def key(self, url): 
        return hashlib.sha256(url.encode("UTF-8")).hexdigest()

    def load_index(self):
        self.index = self.index_file.read_text().split("\n")

    def append_entry(self, url):
        if not url in self.index:
            self.index.append(url)
            with self.index_file.open("a") as outf:
                outf.write(url + "\n")

    def contains(self, url):
        return url in self.index

default_index = CacheIndex(dir=cache_dir)

class Cached:
    def __init__(self, url, index=default_index, ignore_errors=False):
        self.url = url
        self.index = index 
        self.id = index.key(self.url) 
        self.ignore_errors = ignore_errors

    def soup(self):
        return BS(self.get(), "html.parser")

    def cached_path(self):
        return self.index.dir / self.id

    def relative_url(self, path):
        return urljoin(self.url, path)

    def is_cached(self):
        return self.cached_path().exists()

    def clear(self):
        cached = self.cached_path()
        if cached.exists():
            cached.unlink()

    def get(self):
        cached = self.cached_path()
        if cached.exists():
            return cached.read_text()
        else:
            response = requests.get(self.url)
            if response.status_code == 200: 
                cached.write_text(response.text)
                CacheIndex().append_entry(self.url)
                return response.text
            else: 
                logging.error(f"Received error code {response.status_code} from {self.url}")
                if not self.ignore_errors: 
                    raise CrawlerError(self.url)
                else: 
                    return None 
