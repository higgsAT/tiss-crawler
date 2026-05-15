import time

class HttpClient:
	def __init__(self, config):
		self.sleep = config['crawl']['sleep_between_requests']
		self.last_fetch_time = None

	def fetch(self, url):
		"""
		fetch an url while respecting the set time to wait between fetches according to the config
		"""
		wait = 0 # default value when state.json value is None
		if self.last_fetch_time:
			elapsed = time.time() - self.last_fetch_time
			wait = self.sleep - elapsed

		if wait > 0:
			print(f"waiting {wait:.2f}s before making next request")
			time.sleep(wait)

		# ... do request ...
		print(f"TEST: do request: {url}")

		self.last_fetch_time = time.time()


	"""
	#make an initial request to TISS first to establish the session, then subsequent requests will carry the cookies
	session = requests.Session()
	session.headers.update({
		"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
		"Accept-Language": "de"  # or "en" for English
	})
	session.get("https://tiss.tuwien.ac.at")  # establishes session cookies


	session.cookies.set("TISS_LANG", "de")  # or "en"
	"""
