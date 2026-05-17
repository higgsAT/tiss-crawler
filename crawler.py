import argparse
import logging
from pathlib import Path
import sys
import time
import yaml

from src import http_client
from src import logger
from src import state
from src import storage
from src.phases import curricula
from src.phases import courses_discovery

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

	# check if the directories exist
	output_basedir = config["output"]["base_dir"]
	Path(output_basedir).mkdir(parents=True, exist_ok=True)

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
			curricula_page_source = client.fetch(config["crawl"]["url_curricula"], "de")
			extracted_curricula = curricula.fetch_all_curricula(curricula_page_source, output_basedir, semester)
			saved_state['curricula']['queue'] = extracted_curricula
			state.save_state(saved_state, f"{output_basedir}state.json")

		# Phase 2: drain curricula queue
		while saved_state['curricula']['queue']:
			# e.g., curricula_details:
			# ['Weitere Kataloge', 'Professional Skills für Doktorand_innen', '/curriculum/public/curriculum.xhtml?key=74464']
			curricula_details = saved_state['curricula']['queue'].pop(1)
			log.info(f"Process curricula: {curricula_details}")
			courses_discovery.extract_courses(client, config["crawl"]["url_base"], curricula_details, semester, output_basedir)
			# TODO: update saved state via 'state.save_state(saved_state, f"{output_basedir}state.json")'

		# Phase 3: drain courses queue
		while saved_state['courses']['queue']:
			print("third phase")
			# TODO: process discovered courses

	finally:
		client.close()
