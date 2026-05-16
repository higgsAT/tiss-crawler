import logging
from src import http_client
from src import storage

def fetch_all_curricula(
	client: http_client.HttpClient,
	url: str,
	lang: str,
	output_dir: str,
	semester: str
) -> list | None:
	"""
	Fetch all possible curricula availabe at tu wien and return the possible
	urls pointing to each curricula as a list if successful. Returns None upon
	failure.
	"""
	log = logging.getLogger(__name__)
	log.info(f"fetching list of all curricula from url {url} for language {lang}")

	# fetch the page(source)
	response = client.fetch(url, lang)
	page_source = response.text
	print(page_source)

	# save the page source to the disk under:
	# output/
	#   study_programs/
	#     study_programs__<semester>.html
	curricula_dir_write = f"{output_dir}study_programs/"
	filename = f"study_programs__{semester}.html"
	storage.write_to_disk(page_source, curricula_dir_write, filename)
