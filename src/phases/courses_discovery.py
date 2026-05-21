import sys
from urllib.parse import urlparse, parse_qs

import logging
from src import http_client
from src import parser
from src import state
from src import storage

def extract_courses(
	client: http_client.HttpClient,
	url_curricula_endpoint: str,
	curricula_details: dict,
	semester: str,
	output_dir: str
) -> dict:
	"""
	Takes the curricula details as an argument, extracts all corresponding
	courses and returns the extracted information

	Example of curricula_details:
	{
		'url': '/curriculum/public/curriculum.xhtml?key=37047',
		'study_code': '033 243',													<-	may be empty
		'de':
		{
			'name': 'Bachelorstudium Architektur',
			'faculty': 'Architektur'
		},
		'en':
		{
			'name': 'Bachelor programme Architecture',
			'faculty': 'Architecture'
		}
	}
	"""
	# for extraction of just the courses the set language does not matter (use one arbitrarily)
	set_language = "en"

	# build the url -> fetch page for the curricula
	curricula_key = parse_qs(urlparse(curricula_details["url"]).query).get("key", [None])[0]

	# some possible url parameters for curricula:
	# le               ... late enroller (true / false)
	# semesterCode     ... semester, e.g., "2026S"
	# viewAcademicYear ... Semester/Structure-view (former lists courses by semester) -> parameter: true
	# locale           ... language ("de" / "en")
	url_full = f"{url_curricula_endpoint}?le=false&semesterCode={semester}&key={curricula_key}"
	page_source = client.fetch(url_full, set_language)

	# save the page source to the disk under:
	# output/
	#   study_programs/
	#      <program>/                            <-	curricula_details[set_language]["faculty"]
	#         <study_programs>__<semester>.html  <-	curricula_details[set_language]["name"] + semester
	faculty = curricula_details[set_language]["faculty"]
	name = curricula_details[set_language]["name"]
	curricula_source_write = f"{output_dir}study_programs/{faculty}/"
	filename = f"{name}__{semester}.html"
	storage.write_to_disk(page_source, curricula_source_write, filename)

	# extract all courses corresponding to the curricula
	return parser.extract_courses(page_source, semester)
