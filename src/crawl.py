# -*- coding: utf-8 -*-
#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

# TISS login credentials
from config import *

class crawler:
	"""This class contains all functions responsible for crawling webpages.

	All functions build upon webdriver to fetch pages. Among other things,
	the functions in this class are responsible for initiing and closing 
	the webdriver, fetching webpages, etc.
	"""
	def __init__(self, run_headless, non_headless_width, non_headless_height, sleeptime):
		"""The constructor which sets the parameters regarding the webdriver.

		If run_headless is True, webdriver will run in
		headless mode, i.e., no browser window will open
		during program runtime. In case the option is set
		to False, the other two variables define the height
		and width of the the browser window.
		"""
		self.headless = run_headless						# True ... run in headless mode
		self.non_headless_height = non_headless_height		# height of the browser window (if run_headless == False)
		self.non_headless_width = non_headless_width		# width of the browser window (if run_headless == False)
		self.sleeptime_fetchpage = sleeptime				# used in the function fetch_page() to ensure JS has been loaded

	def init_driver(self):
		"""Initiate the webdriver (as defined by the user).

		Using the provided options (headlessness, user agent, browser
		window height and width, etc.), this function initiates the
		webdriver.		
		"""
		print ('initing driver')

		# browser options for chrome
		chrome_options = Options()
		chrome_options.add_argument("--disable-extensions")
		chrome_options.add_argument("--disable-gpu")
		chrome_options.add_argument("--no-sandbox") # linux only
		#chrome_options.add_experimental_option("detach", True)

		# option for running headless (opening a visible browser window or not)
		if self.headless == True:
			chrome_options.add_argument("--headless")

		# set the user agent
		chrome_options.add_argument("user-agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

		# set the driver (chrome)
		driver = webdriver.Chrome(options = chrome_options)

		# set the browser window size (if run_headless == False)
		if self.headless == False:
			driver.set_window_size(self.non_headless_width, self.non_headless_height)

		"""
		Return the handle to keep the browser open over the span
		of the program (else each function call would open and
		close the browser completely)
		"""
		return driver

	def tiss_login(self, driver):
		"""Log in into TISS with the provided user credentials.

		This function performs a login attempt which is verified
		afterwards.
		"""
		print("trying to log in")

		# head to the login page
		URLlogin = "https://idp.zid.tuwien.ac.at/simplesaml/module.php/core/loginuserpass.php?AuthState=_1d7ffb3e1f13ab208155e8e359ef5ce8b081b6202f%3Ahttps%3A%2F%2Fidp.zid.tuwien.ac.at%2Fsimplesaml%2Fsaml2%2Fidp%2FSSOService.php%3Fspentityid%3Dhttps%253A%252F%252Flogin.tuwien.ac.at%252Fauth%26RelayState%3Dhttps%253A%252F%252Flogin.tuwien.ac.at%252Fportal%26cookieTime%3D1654809688"
		driver.get(URLlogin)

		# find username/password field and send the info the input fields
		driver.find_element_by_id("username").send_keys(TissUsername)
		driver.find_element_by_id("password").send_keys(TissPassword)
		
		# click login button
		driver.find_element_by_id("samlloginbutton").click()

		# load this page (else the login won't work correctly)
		page_to_fetch = "https://login.tuwien.ac.at/AuthServ/AuthServ.authenticate?app=76"
		driver.get(page_to_fetch)

		# verify the login (search for logout string in the page source)
		driver.get("https://tiss.tuwien.ac.at")
		search_logout = driver.page_source.find("/admin/authentifizierung/logout")
		#login_page_source = self.fetch_page(driver, page_to_fetch)

		if (search_logout == -1):
			print("login failed")
		else:
			print("login successful")

	def get_language(self, driver):
		"""Function to retrieve the set language.
		
		This function determines from the page source
		which language is set at the moment.
		"""
		language_en_find = driver.page_source.find("language_en")
		language_de_find = driver.page_source.find("language_de")

		if (language_en_find != -1):
			language = "de"
		elif (language_de_find != -1):
			language = "en"
		else:
			# increase wait time to ensure page loading!
			print("unable to determine language - increase page loading")
			language = ""

		return language

	def switch_language(self, driver):
		"""Switch the language (DE/EN).
		
		Switches the set language from EN to DE and
		vice versa, e.g. , when the set language is
		set to EN, this function will switch it to DE.
		"""
		set_language = self.get_language(driver)

		if (set_language == "de"):
			driver.find_element_by_id("language_en").click()
		else:
			driver.find_element_by_id("language_de").click()

		# wait for the page to be loaded correctly (JS)
		sleep(self.sleeptime_fetchpage)

	def fetch_page(self, driver, page):
		"""Fetches a single website using webdriver.

		The arguments of the function are the driver instance object
		as well as the page which should be crawled.
		"""
		print ('fetching page: ', page)

		# fetch the page (open the headless browser)
		driver.get(page)

		"""
		Wait until the javascript code has been delivered. If this
		waiting time is not set, the retrieved page is faulty, i.e., it
		will contain a warning to 'enable JS'. This is due to the fact that
		the page sets a JS cookie, reloads/redirects and this must be resolved
		before fetching the page or it (the fetching) will not succeed!
		"""
		sleep(self.sleeptime_fetchpage)

		inner_div_content = self.verify_page_crawl(driver, page)

		if inner_div_content == "":
			# TODO: increase time, recrawl
			pass

		return inner_div_content

	def verify_page_crawl(self, driver, page):
		"""Check if the retrieved source code (incl. JS) has been fetched properly

		Example error when the page has not been fetched properly (JS error):
		"selenium.common.exceptions.JavascriptException: Message: javascript error:
		Cannot read property 'innerHTML' of null"
		"""

		""" fetch the contents in the targed div (id = contentInner). This
		div contains the information desired for crawling and it should be
		fetched. If the page was crawled too fast, this div does not exist
		since the page looks differently (JS error page). Hence, the try
		block fails when the JS code has not been loaded properly.
		"""
		try:
			inner_div_content = \
				driver.execute_script('return window.document.getElementById("contentInner").innerHTML')
		except:
			print("Error fetching page " + page + " using sleeptime of " +
			str(self.sleeptime_fetchpage))
			inner_div_content = ""	# no contentInner div found. Define it here.

		return inner_div_content

	def fetch_academic_programs(self, driver, URL):
		"""Extract links to academic programs.

		Starting from an URL, this function extracts all
		URLs (hrefs) to all academic programs which serve
		as a starting point for further crawling. All found
		links are stored and returned via a list.
		"""
		fetched_page = self.fetch_page(driver, URL)

		elems = driver.find_elements_by_xpath("//a[@href]")
		found_elements = []

		for elem in elems:
			href_element = elem.get_attribute("href")
			# only select links (hrefs) to academic programs:
			if href_element.find("key") != -1:
				found_elements.append(href_element)

		return found_elements

	def close_driver(self, driver):
		'''Close the webdriver properly.'''
		print ('closing driver')

		driver.close()	# close the current browser window
		driver.quit()	# calls driver.dispose which closes all the browser windows and ends the webdriver session properly
