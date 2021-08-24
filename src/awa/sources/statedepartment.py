
import logging 
import time 

from awa.sources.data_source import DataSource
from awa.cached import Cached 

class DOSPressBriefings(DataSource): 
    def __init__(self, caching=True): 
        DataSource.__init__(self, "State Department Press Briefings", "https://www.state.gov/department-press-briefings/")
        self.caching = caching
    def find_links(self):
        current_url = self.url 
        while current_url is not None: 
            logging.debug(f"Searching {current_url}")
            c = Cached(current_url, cacheable=self.caching) 
            if not c.is_cached(): 
                time.sleep(0.5)
            links = c.links() 
            result_links = [x for x in links if 'collection-result__link' in x.get_attribute_list('class')]
            for result in result_links: 
                yield result.text.strip(), c.relative_url(result.get('href'))
            next_links = [x for x in links if 'next' in x.get_attribute_list('class')]
            if len(next_links) > 0: 
                current_url = c.relative_url(next_links[0].get('href'))
            else: 
                current_url = None 