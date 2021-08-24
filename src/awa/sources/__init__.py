from awa.sources.crs_source import CRSReports
import logging 
import csv
import tqdm

from awa.sources.white_house import WhiteHouseReleases
from awa.sources.crs_source import CRSReports
from awa.sources.statedepartment import DOSPressBriefings
from awa.sources.data_source import (
    AIHRCReports,
    SigarReports,
    AREUReports,
    CentcomQuarterlyReports,
)

source_list = [
    WhiteHouseReleases,
    SigarReports,
    AREUReports,
    CentcomQuarterlyReports,
    AIHRCReports,
    CRSReports,
    DOSPressBriefings, 
]

def configure_logging(): 
    formatter = logging.basicConfig(
        format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=logging.INFO,
    )
    return formatter

def clean_title(title):
    return title.replace("\t", "").replace("\n", "").strip()


def generate_links():
    with tqdm.tqdm(total=len(source_list), position=1) as pbar:
        for source_cls in source_list:
            source = source_cls()
            for title, link in source.find_links():
                yield (source.name, source.url, clean_title(title), link)
            pbar.update(1)


def output_master_csv(path):
    with path.open("wt") as outf:
        csv_writer = csv.writer(outf)
        csv_writer.writerow(["Source Name", "Source URL", "Name", "URL"])
        for source_name, source_url, title, link in generate_links():
            csv_writer.writerow([source_name, source_url, title, link])
