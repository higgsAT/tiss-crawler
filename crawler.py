import argparse
import sys
import yaml

from src import logger
from src import state
from src.phases import studienplaene

def is_numeric(s):
	"""Test if a string represents a number

		For single characters use s.isnumeric()
	"""
	try:
		float(str(s).replace(',', '.'))
		return True
	except ValueError:
		return False

def load_config(config_file: str) -> dict:
	"""
	Load the config file into a dict (which is then returned)
	"""
	with open(config_file) as f:
		loaded_config_file = yaml.safe_load(f)
	return loaded_config_file

def parse_args():
	"""
	Parse the command line arguments using argparse and return the generated <class 'argparse.Namespace'> object
	"""
	parser = argparse.ArgumentParser(description="TISS Crawler")
	parser.add_argument("--semester", type=str, help="Semester to crawl, e.g. 2025W")
	parser.add_argument("--resume", action="store_true", help="Resume from existing state.json")
	return parser.parse_args()

args = parse_args()                 # parse CLI arguments
config = load_config("config.yaml") # load config file
semester = args.semester or config["semester"]      # select semester (CLI arguments overrule config file)
resume = args.resume or config["crawl"]["resume"]   # select resume (if true, continue where crawler stopped. Same overrule as semester)

print(f"select semester: {semester}")
print(f"select resume: {resume}")

# check if the semester has the correct formatting: "2020S" or "2015W"
if len(semester) != 5 or not is_numeric(semester[:4]) or semester[4].isnumeric():
	raise ValueError(f"unsupported format for semester: {semester}")

# set up logging
logger.setup_logger(config["logging"]["level"], config["logging"]["file"])

# load previous state which is being resumed
if resume:
	print("resuming with previous crawl")
# start new: clear everything
else:
	print("starting new crawl")

# fetch studienplaene (study plans)
studienplaene.fetch_studienplaene()

saved_state = state.load_state(f"{config["output"]["base_dir"]}state.json") # load a state from the disk into a variable
print(f"saved_state: {saved_state}")
print(f"saved_state['semester']: {saved_state['semester']}")
print(f"saved_state['study_programs']: {saved_state['study_programs']}")


state.save_state(saved_state, f"{config["output"]["base_dir"]}state.json") # save a state to the disk
