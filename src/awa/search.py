import elasticsearch 

from pprint import pprint 

from awa.cached import default_index, Indexable 

es = elasticsearch.Elasticsearch(['localhost'])

indexable_cache = {} 

def match(word): return { 'match': { 'content': { 'query': word } } }

def all(*queries): return { 'bool': { 'must': queries } }

def any(*queries): return { 'bool': { 'should': queries, 'minimum_should_match': 1 } }

def awa(*terms): return all(*[match(w) for w in terms])

def highlighter(): return { 'fields': { 'content': {} }, 'fragment_size': 500 }

def search(*queries, es=es): 
    result = es.search(index='crawled', size=100, body={'highlight': highlighter(), 'query': awa(*queries)})
    return [ ESHit(h) for h in result['hits']['hits'] ] 

class ESHit: 
    def __init__(self, hit): 
        self._source = { k: hit['_source'][k] for k in hit['_source'] } 
        del(self._source['content']) 
        self.url = self._source['url'] 
        self.id = self._source['id'] 
        self.highlights = hit['highlight']['content']
    def __repr__(self): 
        return self.url
    def indexable(self): 
        if self.url not in indexable_cache: 
            indexable_cache[self.url] = Indexable(self.url) 
        return indexable_cache[self.url] 
    def print(self): 
        pprint(self.url)
        for highlight in self.highlights: 
            rep = highlight.replace('\n', ' ')
            print(f"\t-- {rep}")
        print()
