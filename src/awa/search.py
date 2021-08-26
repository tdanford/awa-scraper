import elasticsearch
import pathlib
import sys
import docker

from pprint import pprint

from awa.cached import default_index, Indexable

es = elasticsearch.Elasticsearch(["localhost"])

indexable_cache = {}


def match(word):
    return {"match": {"content": {"query": word}}}


def all(*queries):
    return {"bool": {"must": queries}}


def any(*queries):
    return {"bool": {"should": queries, "minimum_should_match": 1}}


def awa(*terms):
    return all(*[match(w) for w in terms])


def highlighter():
    return {"fields": {"content": {}}, "fragment_size": 500}


def search(*queries, es=es):
    result = es.search(
        index="crawled",
        size=100,
        body={"highlight": highlighter(), "query": awa(*queries)},
    )
    return [ESHit(h) for h in result["hits"]["hits"]]


class ESHit:
    """An Elasticsearch, which is able to extract highlights"""

    def __init__(self, hit):
        self._source = {k: hit["_source"][k] for k in hit["_source"]}
        del self._source["content"]
        self.url = self._source["url"]
        self.id = self._source["id"]
        self.highlights = hit.get("highlight", {}).get("content", [])

    def __repr__(self):
        return self.url

    def indexable(self):
        if self.url not in indexable_cache:
            indexable_cache[self.url] = Indexable(self.url)
        return indexable_cache[self.url]

    def print(self):
        pprint(self.url)
        for highlight in self.highlights:
            rep = highlight.replace("\n", " ")
            print(f"\t-- {rep}")
        print()


def run_docker(es_version="7.14.0", data_dir=None):
    docker_client = docker.from_env()
    if data_dir is None:
        data_dir = pathlib.Path.cwd() / "elasticsearch"

    if not data_dir.exists():
        if not data_dir.mkdir():
            raise ValueError(
                f"Cannot creato data directory {data_dir.absolute().as_posix()}"
            )

    image_tag = f"docker.elastic.co/elasticsearch/elasticsearch:{es_version}"
    image = docker_client.images.pull(image_tag)

    env = {"discovery.type": "single-node"}
    ports = {9200: 9200, 9300: 9300}
    volumes = {
        data_dir.absolute().as_posix(): {
            "bind": "/usr/share/elasticsearch/data",
            "mode": "rw",
        }
    }
    kwargs = {
        "environment": env,
        "ports": ports,
        "volumes": volumes,
        "remove": True,
        "detach": True,
    }

    return docker_client.containers.run(image_tag, **kwargs)


def follow_logs(container):
    loggen = container.logs(stream=True, follow=True)
    for log in loggen:
        print(log.decode("UTF-8"))


if __name__ == "__main__":
    p = pathlib.Path(sys.argv[1]) / "elasticsearch"
    print(p.absolute().as_posix())
