import logging

def setup_logger(level: str, log_file: str):
	logging.basicConfig(
		level=getattr(logging, level.upper()),
		format="%(asctime)s [%(levelname)s] %(message)s",
		handlers=[
			logging.FileHandler(log_file, encoding="utf-8"),
			logging.StreamHandler()	# console
		]
	)
