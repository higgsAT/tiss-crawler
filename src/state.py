import json
from pathlib import Path

"""
On startup: load state if exists, skip already-fetched items, continue from where it left off.

The state is stored in output/state.json and has the following formatting:
{
  "last_fetch_time": "1778860682.7065003",        <- time of the last page fetch (to ensure sleep_between_requests in config.yaml)
  "semester": "2025W",                            <- requested semester to process
  "curricula": {                                  <- everything related to processing of 'study programs'
    "queue": ["arch_bach", "..."]                 <- list of all possible study programs which will be processed
                                                     to extract all possible courses for this study program and semester
  },
  "courses": {                                    <- everything related to processing of 'courses'
    "queue": ["101.234_DE", "101.234_EN", "..."]  <- found courses (from the step above) which should be processed.
                                                     track english and german courses to ensure both languages are being processed
  }
}
"""

def load_state(path: str) -> dict:
	"""
	Load a state (of the crawler) to continue from this point on.
	"""
	if not Path(path).exists():
		raise FileNotFoundError(f"State file not found: {path}")

	try:
		with open(path) as f:
			return json.load(f)
	except json.JSONDecodeError as e:
		raise ValueError(f"Invalid JSON in state file: {path}") from e

def save_state(state: dict, path: str) -> None:
	"""
	Save a state (of the crawler) to set a point from which can
	be continued in the future.
	"""
	with open(path, 'w') as f:
		json.dump(state, f, indent=2, ensure_ascii=False)

def clear_state(semester: str, path: str) -> None:
	"""
	Clear the state ("clean slate")
	"""
	save_state({
		"semester": semester,
		"curricula": {"queue": []},
		"courses": {"queue": []}
	}, path)

def print_state(state: dict) -> None:
	"""
	Print a state to the console
	"""
	print(f"State: {state}")
