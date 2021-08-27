import logging

from lxml import etree

from awa.data_source import DataSource
from awa.crawler import CrawlingQueue
from awa.cached import Cached


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
        cached = [
            Cached(u, ignore_errors=True, cacheable=False) for u in self.sigar_xml_urls
        ]
        queue = CrawlingQueue(cached, bar_position=0)
        c = 0
        for cached, xml_bytes in queue.crawl():
            try:
                root = etree.fromstring(xml_bytes)
                for item in root.findall("*/item"):
                    title = item.find("title").text
                    relative_link = item.find("link").text.replace("\n", "").strip()
                    full_link = cached.relative_url(relative_link)
                    yield title, full_link
                    c += 1
            except etree.XMLSyntaxError as err:
                logging.error(f"XMLSyntaxError {err}")
                pass
            except AttributeError as err:
                pass
            except ValueError as err:
                pass
        logging.debug(f"# SIGAR Reports: {c}")
