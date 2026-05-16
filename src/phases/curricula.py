import logging

def fetch_all_curricula(url: str, lang: str) -> None:
	"""
	"""
	log = logging.getLogger(__name__)
	log.info(f"fetching list of all curricula from url {url} for language {lang}")
