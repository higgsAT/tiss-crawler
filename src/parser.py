from bs4 import BeautifulSoup

def extract_curricula(page_source: str) -> list | None:
	"""
	Process the page source containing all available curricula using BeautifulSoup.
	Extract the desired information (faculty, curricula_name, curricula_url) and
	return it as a list.
	"""
	soup = BeautifulSoup(page_source, 'html.parser')

	results = []
	for h2 in soup.find_all("h2"):
		faculty = h2.get_text(strip=True)
		table = h2.find_next_sibling("table")
		if table:
			for a in table.find_all("a"):
				name = a.get_text(strip=True)
				url = a["href"]
				results.append((faculty, name, url))

	if len(results) < 10:
		raise RuntimeError("Error extracting curricula")

	return results
