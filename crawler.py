import argparse
import sys
import yaml

from src import logger
from src.phases import studienplaene

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
	parser.add_argument("--semester", type=str, help="Semester to crawl, e.g. WS2025")
	parser.add_argument("--resume", action="store_true", help="Resume from existing state.json")
	return parser.parse_args()


args = parse_args()
config = load_config("config.yaml")

semester = args.semester or config["semester"]
resume = args.resume or config["crawl"]["resume"]

print(f"Semester: {semester}")
print(f"resume: {resume}")

logger.setup_logger(config["logging"]["level"], config["logging"]["file"])

studienplaene.fetch_studienplaene()
