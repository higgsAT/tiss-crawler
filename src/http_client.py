from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
from playwright.sync_api import sync_playwright
import time

import logging

class HttpClient:
	def __init__(self, config) -> None:
		self.sleep = config['crawl']['sleep_between_requests']
		self.last_fetch_time = None
		self.log = logging.getLogger(__name__)
		self._playwright = sync_playwright().start()
		self._browser = self._playwright.chromium.launch(headless=True)
		self._context = self._browser.new_context(viewport={"width": 800, "height": 700})
		self._page = self._context.new_page()

	def _build_url(self, url: str, lang: str) -> str:
		parsed = urlparse(url)
		params = parse_qs(parsed.query, keep_blank_values=True)
		params["locale"] = [lang]
		new_query = urlencode({k: v[0] for k, v in params.items()})
		return urlunparse(parsed._replace(query=new_query))

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

	def _do_request(self, url: str, lang: str) -> str | None:
		"""
		Handle the request and log errors in case they arise.
		"""
		try:
			self._page.goto(self._build_url(url, lang))
			self._page.wait_for_load_state("networkidle")
			return self._page.content()
		except Exception as e:
			self.log.error(f"request failed: {url} — {e}")
			try:
				self.log.error(f"page source at failure:\n{self._page.content()}")
			except Exception:
				self.log.error("could not retrieve page source at failure")
			return None
		finally:
			self.last_fetch_time = time.time()

	def fetch(self, url: str, lang: str) -> str:
		"""
		Fetch an url while respecting the set time to wait between fetches according to the set config.
		Returns the page source upon success
		"""
		self.log.info(f"fetching page: {url} for language {lang}")

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

	def close(self) -> None:
		self._context.close()
		self._browser.close()
		self._playwright.stop()
