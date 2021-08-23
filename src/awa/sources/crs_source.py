
import pathlib 
import csv 

from awa.sources.data_source import DataSource

class CRSReports(DataSource): 
	def __init__(self, path=None): 
		DataSource.__init__(
			self, 
			'CRS Reports',
			'https://crsreports.congress.gov/'
		)
		self.path = path if path is not None else pathlib.Path.cwd() / 'crs-afghanistan-links.csv'
	def find_links(self): 
		with self.path.open('rt') as inf: 
			reader = csv.reader(inf) 
			rows = [x for x in reader] 
		header = rows[0] 
		rows = rows[1:] 
		for row in rows: 
			yield (row[3], row[4]) 
	