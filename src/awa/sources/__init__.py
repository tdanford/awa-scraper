from awa.sources.crs_source import CRSReports
import tqdm
import csv
from awa.sources.white_house import WhiteHouseReleases
from awa.sources.crs_source import CRSReports
from awa.sources.data_source import AIHRCReports, SigarReports, AREUReports, CentcomQuarterlyReports

source_list = [WhiteHouseReleases, SigarReports, AREUReports, CentcomQuarterlyReports, AIHRCReports, CRSReports]


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
        for source_name, source_url, title, link in generate_links():
            csv_writer.writerow([source_name, source_url, title, link])
