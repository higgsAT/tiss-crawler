from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re
import sys

import logging

def extract_curricula(page_source: str, lang: str) -> dict:
	"""
	Process the page source containing all available curricula using BeautifulSoup.
	Extract the desired information (faculty, study_code, curricula_name, curricula_url, lang) and
	return it as a dict.
	"""
	soup = BeautifulSoup(page_source, 'html.parser')

	results = {}
	for h2 in soup.find_all("h2"):
		faculty = h2.get_text(strip=True)
		table = h2.find_next_sibling("table")
		if table:
			for element in table.find_all("tr"):
				# may be empty, for example, for "elective courses" or "transferable skills"
				study_code = element.find("td", {"class": "studyCodeColumn"})
				if study_code:
					study_code = study_code.text.strip()
				else:
					study_code = ""
				study_name_url = element.find("td", {"class": "studyCodeNameColumn"})
				if study_name_url:
					a_tag = study_name_url.find("a")
					if not a_tag:
						continue
					curricula_name = a_tag.get_text(strip=True)
					curricula_url = a_tag["href"]
					key = parse_qs(urlparse(curricula_url).query).get("key", [None])[0]
					if not key:
						continue
				else:
					continue
				results[key] = (faculty, study_code, curricula_name, curricula_url, lang)

	if not results:
		raise RuntimeError("Error extracting curricula")

	return results

def merge_curricula(de: dict, en: dict) -> dict:
	log = logging.getLogger(__name__)
	merged = {}
	for key, (faculty_de, study_code, name_de, url, _) in de.items():
		en_entry = en.get(key)
		if not en_entry:
			log.error(f"Extracting curriculas: Mismatch entries de/en for key: {key}")
			continue
		faculty_en, _, name_en, _, _ = en_entry
		merged[key] = {
			"url": url,
			"study_code": study_code,
			"de": {"name": name_de, "faculty": faculty_de},
			"en": {"name": name_en, "faculty": faculty_en}
		}
	return merged

def extract_courses(page_source: str, semester: str) -> list:
	"""
	Process the page source containing all possible courses for a curricula
	using BeautifulSoup. Extract the desired information (course numbers) and
	return it as a list.

	Make sure the selected semester (from the page source) is the same as
	given as an argument. This value is stored in a dropdown!
	"""
	log = logging.getLogger(__name__)
	soup = BeautifulSoup(page_source, 'html.parser')

	# make sure the right semester is selected in the dropdown menu. The
	# selector may have a different prefix:
	# j_id_2d:semesterSelect
	# j_id_2e:semesterSelect
	# j_id_2f:semesterSelect
	# j_id_2i:semesterSelect
	# -> use a regex selector on ":semesterSelect"
	semester_select_obj = soup.find_all("select", {"id" : re.compile(r'.*:semesterSelect')})
	if len(semester_select_obj) != 1:
		raise RuntimeError(f"Unable to find semester <select> / too many elements found: {semester_select_obj}")
	semester_source = semester_select_obj[0].find("option", {"selected": "selected"}).text.strip()
	if semester_source != semester:
		raise RuntimeError(f"Mismatching semesters -> check source vs. config")





	results = []
	for h2 in soup.find_all("h2"):
		semester = h2.get_text(strip=True)
		print(semester)
		table = h2.find_next_sibling("table")
		if table:
			for a in table.find_all("a"):
				name = a.get_text(strip=True)
				url = a["href"]
				results.append((faculty, name, url))


	sys.exit()


	log.info(f"Extracted {len(results)} courses for semester {semester}")
	if not results:
		log.warning("No courses found for this semester — curricula may be empty for this term")

	return results
