import requests
import re
import time
import logging

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
