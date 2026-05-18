from bs4 import BeautifulSoup
import re
import sys

import logging

def extract_curricula(page_source: str) -> list | None:
	"""
	Process the page source containing all available curricula using BeautifulSoup.
	Extract the desired information (faculty, curricula_name, curricula_url) and
	return it as a list.
	"""
	soup = BeautifulSoup(page_source, 'html.parser')

	results = []
	for h2 in soup.find_all("h2"):
		faculty = h2.get_text(strip=True)
		table = h2.find_next_sibling("table")
		if table:
			for a in table.find_all("a"):
				name = a.get_text(strip=True)
				url = a["href"]
				results.append((faculty, name, url))

	if len(results) < 10:
		raise RuntimeError("Error extracting curricula")

	return results

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
	for course_div in soup.find_all("div", {"class": "courseKey"}):
		parts = course_div.text.strip().split()
		# expected: ['253.G74', 'VO', '2025W']
		if len(parts) != 3:
			raise RuntimeError(f"Unexpected courseKey format: {course_div.text.strip()!r}")
		course_nr, _type, course_semester = parts
		if course_semester == semester:
			results.append(course_nr)

	log.info(f"Extracted {len(results)} courses for semester {semester}")
	if not results:
		log.warning("No courses found for this semester — curricula may be empty for this term")

	return results
