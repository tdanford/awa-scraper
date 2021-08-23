
from awa.sources.white_house import WhiteHouseReleases

source_list = [
	WhiteHouseReleases
]

def generate_links(): 
	for source_cls in source_list: 
		source = source_cls()
		for link in source.find_links(): 
			yield link 