import requests
import os
import pathlib
import hashlib
import logging
import gzip
import base64
import json
import io

from pprint import pprint
from urllib.parse import urljoin
from bs4 import BeautifulSoup as BS
from tqdm import tqdm
from PyPDF2 import PdfFileReader as PDFReader

from awa.crawler import CrawlerError

cache_dir = os.getenv("CACHE_DIR", "cache")


def encode_from_bytes(byte_content):
    """Return a string encoding of the given bytes"""
    if byte_content is None:
        return None
    return base64.b64encode(gzip.compress(byte_content)).decode("UTF-8")


def decode_to_bytes(encoded_content):
    """Decodes a byte array from the given string encoding"""
    if encoded_content is None:
        return None
    return gzip.decompress(base64.b64decode(encoded_content.encode("UTF-8")))


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

    def index_into_elastic(self, es, index_name="crawled"):
        with tqdm(total=len(self.index)) as pbar:
            for u in self.index:
                indexable = Indexable(u)
                indexable.index_into_elastic(es, index=index_name)
                pbar.update(1)

    def clear(self, urls):
        """Clears the given URLs from the cache"""
        self.index = [x for x in self.index if x not in urls]
        for url in urls:
            key = self.key(url)
            path = self.dir / key
            if path.exists():
                path.unlink()
        self.write_index()

    def key(self, url):
        """Calculates the key for a given URL"""
        return hashlib.sha256(url.encode("UTF-8")).hexdigest()

    def load_index(self):
        """Populates the index from the corresponding file backing"""
        self.index = [
            x
            for x in self.index_file.read_text().split("\n")
            if len(x) > 0 and (self.dir / self.key(x)).exists()
        ]

    def write_index(self):
        """Replaces the file backing with the entire contents of the index"""
        with self.index_file.open("wt") as outf:
            for url in self.index:
                outf.write(url + "\n")

    def append_entry(self, url):
        """Adds a new entry to the index"""
        if not url in self.index:
            self.index.append(url)
            with self.index_file.open("a") as outf:
                outf.write(url + "\n")

    def indexables(self):
        return [Indexable(u) for u in self.index]

    def contains(self, url):
        """Returns true if the given URL is in the index"""
        return url in self.index


default_index = CacheIndex(dir=cache_dir)


class Cached:
    def __init__(self, url, index=default_index, ignore_errors=False, cacheable=True):
        self.url = url
        self.index = index
        self.id = index.key(self.url)
        self.ignore_errors = ignore_errors
        self.cacheable = cacheable
        self.headers = None
        self.content = None

    def save(self):
        value = {
            "id": self.id,
            "url": self.url,
            "headers": self.headers,
            "content": encode_from_bytes(self.content),
        }
        self.cached_path().write_text(json.dumps(value))

    def load(self):
        value = json.loads(self.cached_path().read_text())
        self.headers = value.get("headers")
        self.content = decode_to_bytes(value.get("content"))
        assert self.id == value.get("id")
        assert self.url == value.get("url")

    def get_headers(self):
        self.get()
        return self.headers

    def text(self):
        return self.get().decode("UTF-8")

    def soup(self):
        return BS(self.text(), "html.parser")

    def cached_path(self):
        return self.index.dir / self.id

    def relative_url(self, path):
        return urljoin(self.url, path)

    def is_cached(self):
        return self.cached_path().exists()

    def links(self):
        return [x for x in self.soup().find_all("a") if x.get("href") is not None]

    def clear(self):
        cached = self.cached_path()
        if cached.exists():
            cached.unlink()

    def get(self):
        cached = self.cached_path()
        if (
            self.cacheable and cached.exists()
        ):  # only check the cache if the item is cache-able
            if self.content is None:
                self.load()
            return self.content
        else:
            response = requests.get(self.url, headers={"User-Agent": "Mozilla/5.0"})
            self.headers = {k: str(response.headers[k]) for k in response.headers}
            self.content = response.content
            if response.status_code == 200:
                if self.cacheable:  # only cache the result if the item is cache-able
                    self.save()
                    CacheIndex().append_entry(self.url)
                return self.content
            else:
                logging.error(
                    f"Received error code {response.status_code} from {self.url}"
                )
                if not self.ignore_errors:
                    raise CrawlerError(self.url)
                else:
                    return None


class Indexable(Cached):
    def __init__(self, url):
        Cached.__init__(self, url)
        self.get()

    def is_html(self):
        return self.headers.get("Content-Type", "").find("text/html") != -1

    def is_pdf(self):
        return self.headers.get("Content-Type", "").find("pdf") != -1

    def create_document(self):
        doc = {
            "id": self.id,
            "url": self.url,
            "content-type": self.headers.get("Content-Type", "unknown"),
        }
        if self.is_html():
            doc["content"] = self.soup().get_text()
        if self.is_pdf():
            file = io.BytesIO(self.content)
            reader = PDFReader(file)
            pages = [reader.getPage(i) for i in range(reader.numPages)]
            page_text = [page.extractText() for page in pages]
            pdf_text = " ".join(page_text)
            doc["content"] = pdf_text

        return doc

    def index_into_elastic(self, es, index="crawled"):
        es.index(index=index, id=self.id, body=self.create_document())
