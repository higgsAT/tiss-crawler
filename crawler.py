import argparse
import logging
from pathlib import Path
import sys
import time
import yaml

from src import http_client
from src import logger
from src import parser
from src import state
from src import storage
from src.phases import curricula
from src.phases import courses_discovery
from src.phases import courses_crawl

def _load_config(config_file: str) -> dict:
	with open(config_file) as f:
		loaded_config_file = yaml.safe_load(f)
	return loaded_config_file

def _parse_arguments() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="TISS Crawler")
	parser.add_argument("--semester", type=str, help="Semester to crawl, e.g. 2025W")
	parser.add_argument("--resume", action="store_true", help="Resume from existing state.json")
	return parser.parse_args()

if __name__ == "__main__":
	args = _parse_arguments()                           # parse CLI arguments
	config = _load_config("config.yaml")                # load config file
	semester = args.semester or config["semester"]      # select semester (CLI arguments overrule config file)
	resume = args.resume or config["crawl"]["resume"]   # select resume (if true, continue where crawler stopped. Same overrule as semester)

	logger.setup_logger(config["logging"]["level"], config["logging"]["file"])  # set up logging
	log = logging.getLogger(__name__)
	log.info(f"Starting crawler")
	log.info(f"select semester: {semester}")
	log.info(f"select resume: {resume}")

	# check if the semester has the correct formatting: "2020S" or "2015W"
	if len(semester) != 5 or not semester[:4].isdigit() or semester[4] not in ("W", "S"):
		log.error(f"unsupported format for semester: {semester}")
		raise ValueError(f"unsupported format for semester: {semester}")

	# check if the directories exist -> if not: create them
	output_basedir = config["output"]["base_dir"]
	Path(output_basedir).mkdir(parents=True, exist_ok=True)

	output_datadir = config["output"]["data_dir"]
	Path(output_datadir).mkdir(parents=True, exist_ok=True)

	output_coursesdir = config["output"]["courses_dir"]
	Path(output_coursesdir).mkdir(parents=True, exist_ok=True)

	# load previous state which is being resumed
	if resume:
		log.info("resuming with previous crawl")
	# start new: clear everything
	else:
		log.info("starting new crawl -> resetting state.json")
		state.clear_state(semester, f"{output_basedir}state.json")

	# state.clear_state(semester, f"{output_basedir}state.json")	# TEST: reset state

	saved_state = state.load_state(f"{output_basedir}state.json") # load a state from the disk into a variable
	log.info(f"Amount of curricula in queue: {len(saved_state['curricula']['queue'])}")
	log.info(f"Amount of courses in queue: {len(saved_state['courses']['queue'])}")

	# check if the given semester to process via CLI / config.yaml matches the saved state in state.json
	if semester != saved_state['semester']:
		log.error(f"Mismatch between semester in config.yaml/CLI parameter:\
'{semester}' and state.json: '{saved_state['semester']}'")
		raise ValueError(f"Mismatch between semester in config.yaml/CLI parameter:\
'{semester}' and state.json: '{saved_state['semester']}'")

	# initialise http_client object (manages crawling and respects the crawl delay)
	client = http_client.HttpClient(config)

	try:
		# determine at which "phase" the program was stopped:
		# Phase 1: Fetch all curricula
		# Phase 2: Extract courses per curricula
		# Phase 3: Crawl each unique course

		# both queues (study programs and courses) empty -> Phase 1.
		# This assumes a "start from zero" happens.
		if (not saved_state['curricula']['queue'] and
			not saved_state['courses']['queue']):
			# both languages needed here
			curricula_page_source_de = client.fetch(config["crawl"]["url_curricula"], "de")
			extracted_curricula_de = curricula.fetch_all_curricula(curricula_page_source_de, output_basedir, semester, "de")
			curricula_page_source_en = client.fetch(config["crawl"]["url_curricula"], "en")
			extracted_curricula_en = curricula.fetch_all_curricula(curricula_page_source_en, output_basedir, semester, "en")
			curricula_extract = parser.merge_curricula(extracted_curricula_de, extracted_curricula_en)
			saved_state['curricula']['queue'] = curricula_extract
			state.save_state(saved_state, f"{output_basedir}state.json")

		# Phase 2: drain curricula queue
		while saved_state['curricula']['queue']:
			key, entry = saved_state['curricula']['queue'].popitem()
			log.info(f"Process curricula: {entry}")
			extracted_courses = courses_discovery.extract_courses(client, config["crawl"]["url_base_curricula"],
				entry, semester, output_basedir)

			# save the extracted curricula -> courses info into a file in /data/study_programs_<semester>.json
			try:
				curricula_courses_state = state.load_state(f"{output_datadir}study_programs_{semester}.json")
			except FileNotFoundError:
				curricula_courses_state = {}
			for process_semester in extracted_courses:
				dict_key = f"{key}__{process_semester}"
				if dict_key in curricula_courses_state:
					log.warning(f"key '{dict_key}' already in dict")
				curricula_courses_state[dict_key] = {
					"course_numbers": extracted_courses[process_semester],
					"semester": semester,
					"subsemester": process_semester,
					"subprogram_title_de": entry["de"]["name"],
					"subprogram_title_en": entry["en"]["name"],
					"academic_program_de": entry["de"]["faculty"],
					"academic_program_en": entry["en"]["faculty"],
					"program_code": entry["study_code"]
				}

			# make sure there are no duplicate entries in the "courses list" in the saved state
			for process_semester in extracted_courses:
				for course_nr in extracted_courses[process_semester]:
					for lang in ["de", "en"]:
						add_entry = [course_nr, lang]
						if add_entry not in saved_state['courses']['queue']:
							saved_state['courses']['queue'].append(add_entry)

			state.save_state(saved_state, f"{output_basedir}state.json")
			state.save_state(curricula_courses_state, f"{output_datadir}study_programs_{semester}.json")

		# Phase 3: drain courses queue
		while saved_state['courses']['queue']:
			course_number, course_lang = saved_state['courses']['queue'].pop()
			course_data = courses_crawl.process_course(client, output_coursesdir, config["crawl"]["url_course"],
				semester, course_number, course_lang)

			# save the extracted curricula -> courses info into a file in /data/courses_<semester>.json
			courses_state_name = f"{output_datadir}courses_{semester}.json"
			try:
				courses_extract_state = state.load_state(courses_state_name)
			except FileNotFoundError:
				courses_extract_state = {}
			courses_extract_state.setdefault(course_number, {}).setdefault(course_lang, {})
			courses_extract_state[course_number][course_lang] = course_data
			state.save_state(courses_extract_state, courses_state_name)

	finally:
		client.close()
