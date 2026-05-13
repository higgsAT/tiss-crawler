import json
from pathlib import Path

def load_state(path: str) -> dict:
	"""
	Load a state (of the crawler) to continue from this point on.
	"""
	if Path(path).exists():
		with open(path) as f:
			return json.load(f)
	return default_state()

def save_state(state: dict, path: str) -> None:
	"""
	Save a state (of the crawler) to set a point from which can
	be continued in the future.
	"""
	with open(path, 'w') as f:
		json.dump(state, f, indent=2, ensure_ascii=False)

"""
On startup: load state if exists, skip already-fetched items, continue from where it left off.
{
  "semester": "WS2025",
  "study_programs": {
    "fetched": ["arch_bach", "..."],
    "pending": ["..."]
  },
  "courses": {
    "discovered": ["101.234", "..."],
    "fetched_de": ["101.234"],
    "fetched_en": [],
    "pending": ["101.456", "..."]
  }
}
"""
