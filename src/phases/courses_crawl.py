from datetime import datetime

import logging
from src import http_client
from src import parser
from src import storage

def process_course(
	client: http_client.HttpClient,
	output_courses_dir: str,
	course_base_url: str,
	semester: str,
	course_number: str,
	course_lang: str
) -> dict | None:
	log = logging.getLogger(__name__)

	# generate the url with following format:
	# https://tiss.tuwien.ac.at/course/courseDetails.xhtml?semester=2025W&courseNr=299002
	course_url = f"{course_base_url}?courseNr={course_number[0:3]}{course_number[4:]}&semester={semester}"
	log.info(f"process course '{course_url}' with language '{course_lang}'")

	try:
		page_source = client.fetch(course_url, course_lang)
	except RuntimeError:
		log.error(f"Skipping course {course_number} ({course_lang}) after all retries failed")
		return None

	# write page source to disk:
	datestr_now = datetime.now().strftime("%Y-%m-%d")
	courses_dir_write = f"{output_courses_dir}{semester}/"
	filename = f"{course_number}__{course_lang}__{datestr_now}.html"
	storage.write_to_disk(page_source, courses_dir_write, filename)

	return parser.extract_course_details(page_source, semester)
