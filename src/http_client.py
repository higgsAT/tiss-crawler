import requests
import time

import logging

class HttpClient:
	def __init__(self, config) -> None:
		self.sleep = config['crawl']['sleep_between_requests']
		self.last_fetch_time = None
		self.log = logging.getLogger(__name__)

		self.session = requests.Session()
		self.session.headers.update({
			"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0"
		})
		# self.session.get("https://tiss.tuwien.ac.at")  # establish session cookies
		print("GET: https://tiss.tuwien.ac.at")

	def _wait_if_needed(self) -> None:
		"""
		Ensures proper wait time between requests according to the set config
		"""
		wait = 0 # default value for the first crawl (no wait needed here)
		if self.last_fetch_time:
			elapsed = time.time() - self.last_fetch_time
			wait = self.sleep - elapsed

		if wait > 0:
			self.log.info(f"waiting {wait:.2f}s before making next request")
			time.sleep(wait)

	def _do_request(self, url: str, lang: str) -> requests.Response | None:
		"""
		Perform the request. Return the page source or None if an error occurs
		"""
		self.log.info(f"request url: {url} lang: {lang}")

		try:
			response = self.session.get(url, params={"locale": lang})
			response.raise_for_status()  # raises for 4xx/5xx
		except requests.exceptions.RequestException as e:
			self.log.error(f"request failed: {url} — {e}")
			return None

		self.last_fetch_time = time.time()
		return response

	def fetch(self, url: str, lang: str) -> requests.Response:
		"""
		Fetch an url while respecting the set time to wait between fetches according to the set config.
		Returns the page source upon success
		"""
		if lang not in ("de", "en"):
			raise ValueError(f"ValueError for set language: {lang}")

		self._wait_if_needed()

		sleep_time = 120
		amt_retries = 3
		for _ in range(0, amt_retries):
			response = self._do_request(url, lang)
			if response:
				return response

			self.log.info(f"Error fetching page. Set sleeptime set to: {sleep_time} s")
			time.sleep(sleep_time)
			sleep_time *= 2

		# all retries failed -> stop program
		raise RuntimeError(f"Error fetching page. Stopping crawler")
