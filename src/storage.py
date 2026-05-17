from pathlib import Path

import logging

def write_to_disk(source: str, path: str, filename: str) -> None:
	log = logging.getLogger(__name__)
	log.info(f"Try to write to destination '{path}{filename}'")

	# make sure the path exists before writing to it
	Path(path).mkdir(parents=True, exist_ok=True)

	# write the file to the disk
	with open(Path(path) / filename, "w", encoding="utf-8") as f:
		f.write(source)

def read_from_disk(file_path: str | Path) -> str:
	log = logging.getLogger(__name__)
	log.info(f"Reading from '{file_path}'")
	with open(file_path, "r", encoding="utf-8") as f:
		return f.read()
