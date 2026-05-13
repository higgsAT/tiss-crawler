

#make an initial request to TISS first to establish the session, then subsequent requests will carry the cookies

session = requests.Session()
session.headers.update({
	"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
	"Accept-Language": "de"  # or "en" for English
})
session.get("https://tiss.tuwien.ac.at")  # establishes session cookies


session.cookies.set("TISS_LANG", "de")  # or "en"
