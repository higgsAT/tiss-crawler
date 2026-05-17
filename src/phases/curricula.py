import logging
from src import http_client
from src import parser
from src import storage

def fetch_all_curricula(
	page_source: str,
	output_dir: str,
	semester: str
) -> list | None:
	"""
	Fetch all possible curricula availabe at tu wien and return the possible
	urls pointing to each curricula as a list if successful. Returns None upon
	failure.

	Returns a list with following formatting (faculty, curricula_name, curricula_url):
	[
		('Architektur', 'Bachelorstudium Architektur', '/curriculum/public/curriculum.xhtml?key=37047'),
		('Architektur', 'Masterstudium Architektur', '/curriculum/public/curriculum.xhtml?key=41934'),
		('Architektur', 'Masterstudium Building Sciences and Environment', '/curriculum/public/curriculum.xhtml?key=42323'),
		('Architektur', 'Katalog Freie Wahlfächer - Architektur', '/curriculum/public/curriculum.xhtml?key=57488'),
		.
		.
		.
		('Weitere Kataloge', 'Transferable Skills', '/curriculum/public/curriculum.xhtml?key=57214'),
		('Weitere Kataloge', 'Für alle Studierenden', '/curriculum/public/curriculum.xhtml?key=57023'),
		('Weitere Kataloge', 'Austauschmodule Life Sciences', '/curriculum/public/curriculum.xhtml?key=67824'),
		('Weitere Kataloge', 'Professional Skills für Doktorand_innen', '/curriculum/public/curriculum.xhtml?key=74464')
	]
	"""
	log = logging.getLogger(__name__)
	log.info(f"fetching list of all curricula from page source")

	# save the page source to the disk under:
	# output/
	#   study_programs/
	#     study_programs__<semester>.html
	curricula_dir_write = f"{output_dir}study_programs/"
	filename = f"study_programs__{semester}.html"
	storage.write_to_disk(page_source, curricula_dir_write, filename)

	# extract all possible curricula from the page source
	return parser.extract_curricula(page_source)
