from urllib.parse import urljoin
import sys

import logging
from src import http_client
from src import storage

def extract_courses(
	client: http_client.HttpClient,
	url_base: str,
	curricula_details: list,
	semester: str,
	output_dir: str
) -> None:
	"""
	Takes the curricula details as an argument, extracts all corresponding
	courses and returns the extracted information

	Example of curricula_details:
	['Weitere Kataloge', 'Professional Skills für Doktorand_innen', '/curriculum/public/curriculum.xhtml?key=74464']
	"""
	# fetch the curricula page (language does not matter here)
	url_full = urljoin(url_base, curricula_details[2])
	# url_full = "https://higgs.at"
	page_source = client.fetch(url_full, "de")

	# save the page source to the disk under:
	# output/
	#   study_programs/
	#      <program>/										<-	curricula_details[0]
	#         study_programs__<semester>.html		<-	curricula_details[1] + semester
	curricula_source_write = f"{output_dir}study_programs/{curricula_details[0]}/"
	filename = f"{curricula_details[1]}__{semester}.html"
	storage.write_to_disk(page_source, curricula_source_write, filename)

	# extract all courses corresponding to the curricula

	sys.exit()

