"""Pulling and saving copies of remote pages, to the local filesystem 

Precursor to both scraping links and indexing page content into a search engine.
"""

import json
import uuid
import datetime


class PageIndex:
    def __init__(self, root_path):
        self.root_path = root_path
        self.index_path = self.root_path / "index.json"
        self.content_path = self.root_path / "content"
        if self.index_path.exists():
            self.index = json.loads(self.index_path.read_text())
        else:
            self.index = {}

    def save(self):
        with self.index_path.open("wt") as outf:
            outf.write(json.dumps(self.index))

    def index_path(self, url, content=None):
        if not url in self.index:
            self.index[url] = []
        self.index[url].append(IndexElement(url, datetime.datetime.now(), content))


class IndexElement:
    def __init__(self, url, time, content):
        self.url = url
        self.time = time
        self.content = content
        self.id = str(uuid.uuid4())

    def as_dict(self):
        return {
            "url": self.url,
            "time": self.time.isoformat(),
            "content": self.content is not None,
            "id": self.id,
        }

    def to_json(self):
        return json.dumps(self.as_dict())
