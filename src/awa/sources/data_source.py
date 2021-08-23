import requests
import re
from bs4 import BeautifulSoup as BS
from lxml import etree
import time

from tqdm import tqdm 
from urllib.parse import urljoin


class DataSourceError(Exception):
    def __init__(self, source, url, status_code):
        Exception.__init__(self)
        self.source = source
        self.url = url
        self.status_code = status_code


class DataSource:
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def find_links(self):
        return []

class AIHRCReports(DataSource): 
	def __init__(self): 
		DataSource.__init__(
			self, 
			"Afghanistan Independent Human Rights Commission", 
			"https://www.refworld.org/publisher/AIHRC.html"
		)
	def find_links(self): 
		segment_link_pattern = re.compile("AIHRC,+\\d+.html") 
		segment_name_pattern = re.compile('\\d+')
		response = requests.get(self.url) 
		soup = BS(response.text, 'html.parser') 
		links = [x for x in soup.find_all('a') if x.get('href') is not None]
		other_parts = [x for x in links if segment_link_pattern.search(x.get('href')) is not None and segment_name_pattern.search(x.text) is not None]
		urls = [self.url] + [urljoin(self.url, link.get('href')) for link in other_parts] 

		with tqdm(total=len(urls), position=0) as pbar: 
			for url in urls: 
				response = requests.get(url) 
				soup = BS(response.text, 'html.parser') 
				links = [x for x in soup.find_all('a') if x.get('href') is not None and 'itemlink' in x.get_attribute_list('class')] 
				for link in links: 
					title = link.text.strip().replace('\n', '') 
					href = urljoin(url, link.get('href')) 
					yield title, href 
				pbar.update(1) 


class CentcomQuarterlyReports(DataSource): 
	def __init__(self): 
		DataSource.__init__(self, "CENTCOM Quarterly Contractor Census Reports", "https://www.acq.osd.mil/log/ps/CENTCOM_reports.html") 
		self.urls = [
			"https://www.acq.osd.mil/log/ps/CENTCOM_reports.html", 
			"https://www.acq.osd.mil/log/PS/archvd_CENTCOM_reports.html"
		]	
	def find_links(self): 
		with tqdm(total=len(self.urls), position=0) as pbar: 
			for url in self.urls: 
				response = requests.get(url) 
				soup = BS(response.text, 'html.parser') 
				links = [x for x in soup.find_all('a') if x.get('href').endswith('pdf')]
				for link in links: 
					title = link.get('href').split('/')[-1]
					link = urljoin(url, link.get('href')) 
					yield title, link 
				pbar.update(1) 


class SigarReports(DataSource):
	def __init__(self):
		DataSource.__init__(
            self, "SIGAR Reports", "https://www.sigar.mil/allreports/index.aspx?SSR=5"
        )
		self.sigar_xml_urls = [
            "https://www.sigar.mil/Newsroom/spotlight/spotlight.xml",
            "https://www.sigar.mil/Newsroom/pressreleases/press-releases.xml",
            "https://www.sigar.mil/Newsroom/testimony/testimony.xml",
            "https://www.sigar.mil/Newsroom/speeches/speeches.xml",
            "https://www.sigar.mil/audits/auditreports/reports.xml",
            "https://www.sigar.mil/audits/evaluationreports/evaluation-reports.xml",
            "https://www.sigar.mil/audits/inspectionreports/inspection-reports.xml",
            "https://www.sigar.mil/audits/financialreports/Financial-Audits.xml",
            "https://www.sigar.mil/SpecialProjects/reviews/reviews.xml",
            "https://www.sigar.mil/SpecialProjects/factsheets/fact-sheets.xml",
            "https://www.sigar.mil/SpecialProjects/mgmtandalertletters/mgmt-alert-letters.xml",
            "https://www.sigar.mil/SpecialProjects/inquiryletters/inquiry-letters.xml",
            "https://www.sigar.mil/SpecialProjects/otherpublications/other-publications.xml",
            "https://www.sigar.mil/investigations/alert-special-reports.xml",
            "https://www.sigar.mil/Audits/alertandspecialreports/alert-special-reports.xml",
            "https://www.sigar.mil/quarterlyreports/index.xml",
            "https://www.sigar.mil/LessonsLearned/LessonsLearnedReports/lessons-learned-reports.xml",
        ]

	def find_links(self):
		with tqdm(total=len(self.sigar_xml_urls), position=0) as pbar:
			for xml_url in self.sigar_xml_urls:
				time.sleep(0.15)
				try:
					response = requests.get(xml_url)
					if response.status_code == 200:
						root = etree.fromstring(response.text.encode("utf-8"))
						for item in root.findall("*/item"):
							title = item.find("title").text
							relative_link = item.find("link").text.replace('\n', '').strip()
							full_link = urljoin(xml_url, relative_link)
							yield title, full_link
					pbar.update(1)
				except etree.XMLSyntaxError as err:
					pass


class AREUReports(DataSource):
    def __init__(self):
        DataSource.__init__(self, "AREU Reports", "https://areu.org.af/publications/")

    def find_links(self):
        search_url = "https://areu.org.af/publications/?keyword=afghanistan"
        response = requests.get(search_url)
        if response.status_code != 200:
            raise DataSourceError(self, search_url, response.status_code)
        soup = BS(response.text, "html.parser")
        links = [x for x in soup.find_all("a") if x.get("download") is not None]
        for link in links:
            yield link.get("download"), link.get("href")
