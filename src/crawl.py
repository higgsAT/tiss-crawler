# -*- coding: utf-8 -*-
#!/usr/bin/python3

import os
import random
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.common.exceptions import NoSuchElementException
import sys
import time
import warnings

from config import *
import pylogs

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
		self.headless = run_headless							# True ... run in headless mode
		self.non_headless_height = non_headless_height	# height of the browser window (if run_headless == False)
		self.non_headless_width = non_headless_width		# width of the browser window (if run_headless == False)
		self.sleeptime_fetchpage = sleeptime				# used in the function fetch_page() to ensure JS has been loaded
		self.language = ""										# set language (de/en) used by extract_course_info(...)
		self.crawl_delay = sleeptime							# crawl delay in seconds
		self.last_crawltime = time.time()					# last time a page has been fetched (t_init = t_start)
		self.download_path_root = download_folder			# dir for download folder (set in config.py)
		self.download_path_temp = "temp/"					# dir where files will be downloaded temporarily
		self.logged_in = False									# login-state, manipulated by self.tiss_login(...)

	def init_driver(self):
		"""Initiate the webdriver (as defined by the user).

		Using the provided options (headlessness, user agent, browser
		window height and width, etc.), this function initiates the
		webdriver.
		"""

		# firefox browser options
		opts = FirefoxOptions()

		opts.set_preference("browser.download.folderList", 2)
		opts.set_preference("browser.download.manager.showWhenStarting", False)
		opts.set_preference("browser.download.dir", self.download_path_root + self.download_path_temp)
		opts.set_preference("browser.helperApps.alwaysAsk.force", False);
		opts.set_preference("browser.download.manager.useWindow", False);
		opts.set_preference("browser.download.manager.focusWhenStarting", False);
		opts.set_preference("browser.download.manager.alertOnEXEOpen", False);
		opts.set_preference("browser.download.manager.showAlertOnComplete", False);
		opts.set_preference("browser.download.manager.closeWhenDone", True);
		opts.set_preference("pdfjs.disabled", True);

		mime_types = [
		    'text/plain',
		    'application/vnd.ms-excel',
		    'text/csv',
		    'application/csv',
		    'text/comma-separated-values',
		    'application/download',
		    'application/octet-stream',
		    'binary/octet-stream',
		    'application/binary',
		    'application/x-unknown'
		]
		opts.set_preference("browser.helperApps.neverAsk.saveToDisk", ",".join(mime_types))

		# set the user agent
		opts.set_preference("general.useragent.override", "userAgent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

		# option for running headless (opening a visible browser window or not)
		if self.headless == True:
			opts.add_argument("--headless")

		# set the browser window size (if run_headless == False)
		if self.headless == False:
			opts.add_argument("--width=" + str(self.non_headless_width))
			opts.add_argument("--height=" + str(self.non_headless_height))

		driver = Firefox(options = opts)

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

		self.get_page(driver, URLlogin)

		# find username/password field and send the info the input fields
		driver.find_element("name", "username").send_keys(TissUsername)
		driver.find_element("name", "password").send_keys(TissPassword)

		# click login button
		driver.find_element("id", "samlloginbutton").click()

		# load this page (else the login won't work correctly)
		page_to_fetch = "https://login.tuwien.ac.at/AuthServ/AuthServ.authenticate?app=76"
		self.fetch_page(driver, page_to_fetch)

		# verify the login (search for logout string in the page source)
		self.fetch_page(driver, "https://tiss.tuwien.ac.at")
		search_logout = driver.page_source.find("/admin/authentifizierung/logout")
		#login_page_source = self.fetch_page(driver, page_to_fetch)

		if (search_logout == -1):
			print("login failed")
		else:
			print("login successful")
			self.logged_in = True

	def get_language(self, driver):
		"""Function to retrieve the set language.
		
		This function determines from the page source
		which language is set at the moment.
		"""

		# if the user initiates the driver and calls this function
		# immediately, no page is loaded and this if statement returns true
		if driver.page_source == "<html><head></head><body></body></html>":
			print("no previous page loaded")
			# load the default (tiss)page to determine the language
			self.fetch_page(driver, "https://tiss.tuwien.ac.at/curriculum/studyCodes.xhtml")

		# different needles for different pages
		language_en_find = driver.page_source.find("language_en")
		language_en_find2 = driver.page_source.find('<a href="/?locale=en">English</a>')

		language_de_find = driver.page_source.find("language_de")
		language_de_find2 = driver.page_source.find('<a href="/?locale=de">Deutsch</a>')

		if (language_en_find != -1 or language_en_find2 != -1):
			language = "de"
		elif (language_de_find != -1 or language_de_find2 != -1):
			language = "en"
		else:
			# TODO: increase wait time to ensure page loading / retry!
			print("unable to determine language")
			language = ""

		return language

	def switch_language(self, driver):
		"""Switch the language (DE/EN).
		
		Switches the set language from EN to DE and
		vice versa, e.g. , when the set language is
		set to EN, this function will switch it to DE.

		TODO: the link to switch languages seems to differ
		sometimes (e.g., id="toolNavFormLang").
		"""
		set_language = self.get_language(driver)

		# different needles for different pages
		language_en_find = driver.page_source.find("language_en")
		language_en_find2 = driver.page_source.find('<a href="/?locale=en">English</a>')

		language_de_find = driver.page_source.find("language_de")
		language_de_find2 = driver.page_source.find('<a href="/?locale=de">Deutsch</a>')

		if (set_language == "de" and language_en_find != -1):
			driver.find_element("id", "language_en").click()
			self.language = "en"

		if (set_language == "de" and language_en_find2 != -1):
			driver.find_element(By.XPATH,'//a[contains(@href,"/?locale=en")]').click()
			self.language = "en"

		if (set_language == "en" and language_de_find != -1):
			driver.find_element("id", "language_de").click()
			self.language = "de"

		if (set_language == "en" and language_de_find2 != -1):
			driver.find_element(By.XPATH,'//a[contains(@href,"/?locale=de")]').click()
			self.language = "de"

		# wait for the page to be loaded correctly (JS)
		time.sleep(self.sleeptime_fetchpage)

	def get_page(self, driver, page):
		"""Fetch a single page while respecting time delay between crawls.

		Every page crawl is routed through this function to ensure that
		a certain amount of time has passed between each call. This does not
		respect other interactions (e.g., select events) but since a lot relies
		on JS to be fetched, the delay is considered inherently in these cases.
		"""
		t_diff = time.time() - self.last_crawltime

		if t_diff < self.crawl_delay:
			time.sleep(self.crawl_delay - t_diff)

		self.last_crawltime = time.time()
		driver.get(page)

	def fetch_page(self, driver, page):
		"""Fetches a single website and verify its crawl.

		The arguments of the function are the driver instance object
		as well as the page which should be crawled.
		"""
		print ('fetching page: ', page)

		# fetch the page (open the headless browser)
		self.get_page(driver, page)

		"""
		Wait until the javascript code has been delivered. If this
		waiting time is not set, the retrieved page is faulty, i.e., it
		will contain a warning to 'enable JS'. This is due to the fact that
		the page sets a JS cookie, reloads/redirects and this must be resolved
		before fetching the page or it (the fetching) will not succeed!
		"""
		time.sleep(self.sleeptime_fetchpage)

		inner_div_content = self.verify_page_crawl(driver, page)

		# no page loading at all
		i = 2
		while inner_div_content == "":
			time.sleep(i * self.sleeptime_fetchpage)
			driver.refresh()
			inner_div_content = self.verify_page_crawl(driver, page)
			i = i + 2
			print("failed to load content -> " + str(i))
			if i > 20:
				break

		# error loading javascript
		i = 2
		while inner_div_content.find("Something went seriously wrong Please try refreshing the page") != -1:
			time.sleep(i * self.sleeptime_fetchpage)
			driver.refresh()
			inner_div_content = self.verify_page_crawl(driver, page)
			i = i + 2
			print("failed to load (JS) content -> " + str(i))
			if i > 20:
				break

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

	def extract_hrefs(self, haystack, superior_title):
		"""

		<a href="/curriculum/public/curriculum.xhtml?key=41934">Masterstudium Architektur </a>
		->
		[https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=41934|superior_title|Masterstudium Architektur]
		"""
		divider1 = '<a href="'
		divider2 = '">'
		divider3 = '</a>'

		url_prefix = 'https://tiss.tuwien.ac.at'
		return_data = []

		while haystack.find(divider1) != -1:
			position1 = haystack.find(divider1)

			haystack = haystack[position1 + len(divider1):]

			position2 = haystack.find(divider2)
			position3 = haystack.find(divider3)

			string_part1 = url_prefix + haystack[:position2]
			string_part2 = haystack[position2 + len(divider2):position3].strip()

			return_data.append(string_part1 + "|" + superior_title + "|" + string_part2)

			haystack = haystack[position3 + len(divider3):]

		return return_data

	def extract_academic_programs(self, driver, URL):
		"""Extract links and informations to academic programs.

		"""
		fetched_page = self.fetch_page(driver, URL)

		divider1 = "<h2>"
		divider2 = "</h2>"

		position1 = fetched_page.find(divider1)

		fetched_page = fetched_page[position1 + len(divider1):]

		return_collected_data = []

		while fetched_page.find(divider1) != -1:
			position1 = fetched_page.find(divider1)
			position2 = fetched_page.find(divider2)

			superior_title = fetched_page[:position2]

			haystack = fetched_page[:fetched_page.find(divider1)]
			extracted_links = self.extract_hrefs(haystack, superior_title)
			return_collected_data.extend(extracted_links)

			fetched_page = fetched_page[position1 + len(divider1):]

		# process rest of the string
		fetched_page = fetched_page[:fetched_page.find('<div id="footer">')]
		position2 = fetched_page.find(divider2)
		superior_title = fetched_page[:position2]
		extracted_links = self.extract_hrefs(fetched_page, superior_title)
		return_collected_data.extend(extracted_links)

		return return_collected_data

	def extract_courses(self, driver, URL, pylogs_filepointer):
		"""Extract courses from the (study) program.

		This function loops through all years (HTML select element)
		and extracts all the links (URLs) to the courses from the
		course program / overview.

		To do this, the function takes the URL to a academic program
		and extracts the URLs to the courses for each semester. Finally,
		duplicates are removed from the list (extracted_course_URLs) and
		it is being returned by the function.
		"""
		# fetch the online academic program
		self.fetch_page(driver, URL)
		time.sleep(self.sleeptime_fetchpage)

		# selector element for year(semester) selection
		search_selector1 = driver.page_source.find("j_id_2d:semesterSelect")
		search_selector2 = driver.page_source.find("j_id_2e:semesterSelect")

		if search_selector1 != -1:
			selector = Select(driver.find_element("name", "j_id_2d:semesterSelect"))
			pylogs.write_to_logfile(pylogs_filepointer, 'selected selector1: j_id_2d:semesterSelect')
		elif search_selector2 != -1:
			selector = Select(driver.find_element("name", "j_id_2e:semesterSelect"))
			pylogs.write_to_logfile(pylogs_filepointer, 'selected selector1: j_id_2e:semesterSelect')
		else:
			pylogs.write_to_logfile(pylogs_filepointer, 'no selector1 found (2d/2e)')

		extracted_course_URLs = []

		#for i in selector.options:
		    #print(i.get_attribute('innerHTML'))

		# loop through all semesters and store all links to the courses
		for index in range(len(selector.options)):
			search_selector1 = driver.page_source.find("j_id_2d:semesterSelect")
			search_selector2 = driver.page_source.find("j_id_2e:semesterSelect")

			if search_selector1 != -1:
				#selector = Select(driver.find_element("name", "j_id_2d:semesterSelect"))
				pylogs.write_to_logfile(pylogs_filepointer, 'selected selector2: j_id_2d:semesterSelect')
				select = Select(driver.find_element("name", "j_id_2d:semesterSelect"))
			elif search_selector2 != -1:
				selector = Select(driver.find_element("name", "j_id_2e:semesterSelect"))
				pylogs.write_to_logfile(pylogs_filepointer, 'selected selector2: j_id_2e:semesterSelect')
				select = Select(driver.find_element("name", "j_id_2e:semesterSelect"))
			else:
				pylogs.write_to_logfile(pylogs_filepointer, 'no selector2 found (2d/2e)')

			select.select_by_index(index)
			time.sleep(self.sleeptime_fetchpage)

			# extract all links foundstarting downloading files
			elems = driver.find_elements(By.XPATH, "//a[@href]")

			for elem in elems:
				href_element = elem.get_attribute("href")
				if href_element.find("courseDetails") != -1:
					extracted_course_URLs.append(href_element)

		# remove years so that only the courses remain. Later on, years
		# will be crawled individually.
		for i in range(len(extracted_course_URLs)):
			cut_pos = extracted_course_URLs[i].find("&semester=")
			extracted_course_URLs[i] = extracted_course_URLs[i][:cut_pos]

		# remove duplicate URLs from the links
		extracted_course_URLs = list( dict.fromkeys(extracted_course_URLs) )

		return extracted_course_URLs

	def extract_course_info(
		self,
		driver,
		URL,
		academic_program_name,
		acad_prgm_studycode,
		pylogs_filepointer,
		f_failed_downloads,
		download_files = False
	):
		"""Process a single course and extract relevenat information.
		"""

		# number of processed semesters for this course (e.g., processing: 2021W, 2021S yields 2)
		amt_of_semesters_processed = 0

		# create path for the source files
		acad_program_page_sources_path = (root_dir + logging_folder +
			academic_program_name + ' - ' + acad_prgm_studycode
		)

		# total amount of downloaded files for this course
		amount_downloads = 0

		# determine/set the language (ger/en)
		if not self.language:
			self.language = self.get_language(driver)

		# determine course number from the (given) URL
		needle = "courseNr="
		course_number_URL = URL[URL.find(needle) + len(needle):]
		#print("URL course number: " + course_number_URL)

		# dict containing all the extracted information of one semester
		extract_dict = {}

		# store the available semesters (2012W, 2013W, etc.) for this course
		# the index is the semester, the corresponding data marks optional
		# download data (links)
		semester_list = {}

		# stacked dict with indices being semesters and each data the semester_list.
		# This data will also be returned from this function
		return_info_dict = {}

		## fetch semester option info
		# fetch page (to get the option informations)
		self.fetch_page(driver, URL)

		course_not_available1 = driver.page_source.find("The Course is not public in semester")
		course_not_available2 = driver.page_source.find("Bitte wählen Sie ein anderes Semester aus")

		selector_j_26 = False

		if course_not_available1 == -1 and course_not_available2 == -1:
			source_selector_j25 = driver.page_source.find("semesterForm:j_id_25")
			source_selector_j26 = driver.page_source.find("semesterForm:j_id_26")

			if source_selector_j25 != -1:
				selector = Select(driver.find_element("name", "semesterForm:j_id_25"))
			elif source_selector_j26 != -1:
				selector = Select(driver.find_element("name", "semesterForm:j_id_26"))
			else:
				print("neither j_id_25 nor j_id_26 selector was found")

		else:
			# Caused by not being logged in ?! - not likely
			# course not available, selector is therefore not to be found -> try refreshing
			pylogs.write_to_logfile(pylogs_filepointer, 'course not available1 (' + str(course_not_available1) +
				'); course not available2 ( ' + str(course_not_available2) + ') -> rerouting'
			)
			#driver.refresh()
			#time.sleep(self.sleeptime_fetchpage)
			driver.find_element("id", "j_id_2c:j_id_2n").click()
			time.sleep(self.sleeptime_fetchpage)
			#selector = Select(driver.find_element("name", "semesterForm:j_id_25"))

			# reroute to selector j_id_26
			source_selector_j_26 = driver.page_source.find("semesterForm:j_id_26")

			pylogs.write_to_logfile(pylogs_filepointer, 'source_selector_j_26: ' + str(source_selector_j_26))

			if source_selector_j_26 != -1:
				selector = Select(driver.find_element("name", "semesterForm:j_id_26"))
				selector_j_26 = True

		# used for download folder names. Should always be set to german.
		course_title_download_ger = ""

		unknown_fields = []

		# loop through all semesters, extract the desired information
		for option in selector.options:
			semester_option_text = option.text
			semester_option_attribute = option.get_attribute('value')
			semester_list[semester_option_attribute] = ""
			#print(semester_option_text + "|" + semester_option_attribute)

		semester_iterate_list = list(semester_list.keys())

		pylogs.write_to_logfile(pylogs_filepointer, 'semester_iterate_list: ' + str(semester_iterate_list))

		for select_semester in range(len(semester_iterate_list)):
			#print("selecting: " + semester_iterate_list[select_semester])

			# try to fetch the select element
			try:
				select = Select(driver.find_element("name", "semesterForm:j_id_25"))
			except NoSuchElementException:
				pylogs.write_to_logfile(pylogs_filepointer, "no element j_id_25")

				try:
					select = Select(driver.find_element("name", "semesterForm:j_id_26"))
				except NoSuchElementException:
					pylogs.write_to_logfile(pylogs_filepointer, "no element j_id_26")

			select.select_by_visible_text(semester_iterate_list[select_semester])
			time.sleep(self.sleeptime_fetchpage)

			selected_semester = semester_iterate_list[select_semester]

			# get both languages
			for i in range(0, 2):
				# always start with the same language (download folder name)
				if i == 1:
					self.switch_language(driver)
				"""
				if i == 0 and self.language != "de":
					self.switch_language(driver)
				else:
					self.switch_language(driver)
				"""

				#print("i: " + str(i) + "  |  set language: " + self.language)

				pylogs.write_to_logfile(pylogs_filepointer, 'open URL: ' + URL +
					' | lang: ' + self.language +
					' | selected_semester: ' + str(selected_semester)
				)
				course_raw_info = self.fetch_page(driver, URL)
				amt_of_semesters_processed += 1

				# check if materials are available for download
				#found_materials = False

				if course_raw_info.find("Zu den Lehrunterlagen") != -1 and i == 0:
					#pos_LU = course_raw_info.find("Zu den Lehrunterlagen")
					#print("materialsDE")
					semester_list[selected_semester] = ("https://tiss.tuwien.ac.at/education/course/documents.xhtml?courseNr=" +
						str(course_number_URL) + "&semester=" + str(semester_iterate_list[select_semester])
					)
					#found_materials = True
				if course_raw_info.find("Go to Course Materials") != -1 and i == 0:
					#pos_LU = course_raw_info.find("Go to Course Materials")
					#print("materialsEN")
					semester_list[selected_semester] = ("https://tiss.tuwien.ac.at/education/course/documents.xhtml?courseNr=" +
						str(course_number_URL) + "&semester=" + str(semester_iterate_list[select_semester])
					)
					#found_materials = True

				# clear all data in the dict
				extract_dict = {}

				## extract the data
				extract_dict["page_fetch_lang"] = self.language

				# course number and course title
				needle1 = '<span class="light">'
				pos1 = course_raw_info.find(needle1)
				needle2 = "</span>"
				pos2 = course_raw_info.find(needle2)
				course_number = course_raw_info[pos1 + len(needle1):pos2].strip()
				#print("course nmbr: |" +  course_number + "|")
				extract_dict["course number"] = course_number

				# sanity course number check
				if course_number_URL != course_number.replace('.', ''):
					warnings.warn("Error mismatching course numbers: " +
						course_number.replace('.', '') + " and " + course_number_URL
					)
					print("FP1: " + course_raw_info)
					time.sleep(30)
					course_raw_info = self.fetch_page(driver, URL)
					print("FP2: " + course_raw_info)

				course_raw_info = course_raw_info[pos2 + len(needle2):]
				#print(course_raw_info)

				needle3 = "<"
				pos3 = course_raw_info.find(needle3)
				course_title = course_raw_info[:pos3].strip()
				#print("course title: |" + course_title + "|")
				extract_dict["course title"] = course_title

				pylogs.dump_to_log(acad_program_page_sources_path + '/' + course_number_URL + '|' + self.language + '|' + selected_semester + '|' + pylogs.get_time() + '|'+ course_title.replace("/", "") + '.txt', course_number_URL + '|' + self.language + '|' + selected_semester + '|' + pylogs.get_time() + '|'+ course_title + '\n\n\n' + course_raw_info)

				if (course_title_download_ger == "" and self.language == "de"):
					course_title_download_ger = course_title

				# quickinfo
				needle4 = '<div id="subHeader" class="clearfix">'
				pos4 = course_raw_info.find(needle4)
				needle5 = "</div>"
				pos5 = course_raw_info.find(needle5)
				quickinfo = course_raw_info[pos4 + len(needle4):pos5].strip()
				#print("quickinfo: |" + quickinfo + "|")

				quickinfo_split = quickinfo.split(',')
				extract_dict["semester"] = quickinfo_split[0].strip()
				extract_dict["type"] = quickinfo_split[1].strip()
				extract_dict["sws"] = quickinfo_split[2].strip()
				extract_dict["ECTS"] = quickinfo_split[3].strip()
				# quickinfo examples:
				# 2014W, PR, 3.0h, 3.0EC, to be held in blocked form
				# 2015W, UE, 1.0h, 2.0EC
				# the last entry is optional
				if len(quickinfo_split) > 4:
					extract_dict["add_info"] = quickinfo_split[4].strip()
				else:
					extract_dict["add_info"]  = ""

				# certain sections may be present multiple times in the page. Therefore, count
				# how many times they are present and add the integer count to the dict index.
				count_entry_dict = {}
				count_entry_dict["Additional information"] = 0
				count_entry_dict["Weitere Informationen"] = 0

				# language dict so that en and de versions have the same index in
				# the returned dict. This is essential for insertion into the database
				index_dict_en = {
					"Properties": "Merkmale",
					"Learning outcomes": "Lernergebnisse",
					"Additional information": "Weitere Informationen",
					"Subject of course": "Inhalt der Lehrveranstaltung",
					"Teaching methods": "Methoden",
					"Mode of examination": "Prüfungsmodus",
					"Examination modalities": "Leistungsnachweis",
					"Course registration": "LVA-Anmeldung",
					"Literature": "Literatur",
					"Previous knowledge": "Vorkenntnisse",
					"Preceding courses": "Vorausgehende Lehrveranstaltungen",
					"Lecturers": "Vortragende Personen",
					"Language": "Sprache",
					"Institute": "Institut",
					"Group dates": "Gruppentermine",
					"Exams": "Prüfungen",
					"Group Registration": "Gruppen-Anmeldung",
					"Course dates": "LVA Termine",
					"Curricula": "Curricula",
					"Aim of course": "Ziele der Lehrveranstaltung"
				}

				# "<h2>-extraction" - each information is separated by an h2 element
				needle6 = "<h2>"

				i = 0

				while course_raw_info.find(needle6) != -1:
					pos6 = course_raw_info.find(needle6)
					course_raw_info = course_raw_info[pos6 + len(needle6):]

					#print(str(i) + "########################################")

					if course_raw_info.find(needle6) != -1:
						pos7 = course_raw_info.find(needle6)
						extract_info = course_raw_info[:pos7]
					else:
						extract_info = course_raw_info

					#header
					header_needle = "</h2>"
					header_pos = extract_info.find(header_needle)
					header_titletext = extract_info[:header_pos]

					#print(header_titletext + ":")

					extract_info = extract_info[header_pos + len(header_needle):]

					# html cleanup
					extract_info = extract_info.replace(' class="encode"', '')
					extract_info = extract_info.replace(' class="bulletList"', '')

					if self.language == "en":
						#print("Searching for in dict: " + header_titletext)
						if header_titletext in index_dict_en:
							header_titletext = index_dict_en[header_titletext]
						else:
							warnings.warn("Error key is missing: " + header_titletext)

					if header_titletext == "Merkmale":
						extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
						extract_info = ""

					if header_titletext == "Ziele der Lehrveranstaltung":
						extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
						extract_info = ""

					if header_titletext == "Lernergebnisse":
						extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
						extract_info = ""

					if header_titletext == "Inhalt der Lehrveranstaltung":
						extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
						extract_info = ""

					if header_titletext == "Methoden":
						extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
						extract_info = ""

					if header_titletext == "Prüfungsmodus":
						extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
						extract_info = ""

					if header_titletext == "Leistungsnachweis":
						extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
						extract_info = ""

					if header_titletext == "LVA-Anmeldung":
						extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
						extract_info = ""

					if header_titletext == "Literatur":
						extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
						extract_info = ""

					if header_titletext == "Vorkenntnisse":
						extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
						extract_info = ""

					if header_titletext == "Vorausgehende Lehrveranstaltungen":
						extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
						extract_info = ""

					if header_titletext == "Vortragende Personen":
						extract_dict[header_titletext] = self.extract_course_info_lecturers(extract_info)
						extract_info = ""

					add_info_flag = False
					if header_titletext == "Weitere Informationen":
						add_info_flag = True
						past_entries = count_entry_dict["Weitere Informationen"]

						extract_dict[header_titletext + str(past_entries)] = extract_info.replace('\n', '').strip()
						extract_info = ""
						count_entry_dict["Weitere Informationen"] += 1

					if header_titletext == "Sprache":
						cut_str = '<input type="hidden" name='
						cut_pos = extract_info.find(cut_str)
						extract_dict[header_titletext] = extract_info[:cut_pos]
						extract_info = ""

					if header_titletext == "Curricula":
						extract_dict[header_titletext] = self.extract_course_info_curricula(extract_info)
						extract_info = ""

					if header_titletext == "Institut":
						needle = '<li><a href='
						pos1 = extract_info.find(needle)
						extract_info = extract_info[pos1 + len(needle):]
						extract_info = extract_info[extract_info.find('>') + 1:]
						extract_dict[header_titletext] = extract_info[:extract_info.find('<')].replace('\n', '').strip()
						extract_info = ""

					if header_titletext == "Gruppentermine":
						#TODO: extract this information
						course_exams_info = ""
						#extract_info = ""

					if header_titletext == "Prüfungen":
						#TODO: extract this information
						course_exams_info = ""
						extract_info = ""

					if header_titletext == "Gruppen-Anmeldung":
						#TODO: extract this information
						course_exams_info = ""
						extract_info = ""

					if header_titletext == "LVA Termine":
						#TODO: extract this information
						course_coursedate_info = ""
						extract_info = ""

					if extract_info != "":
						warnings.warn("Error processing course description (unkown field) " + header_titletext)
						unknown_fields.append(header_titletext + "|" + course_number + "|" +
							self.language + "|" + academic_program_name + "|" + course_title
						)

					i += 1

					if i > 100:
						break

				return_info_dict[selected_semester + self.language] = extract_dict

		# download files
		amount_downloads = self.download_course_files(
			driver,
			course_number_URL,
			course_title_download_ger,
			semester_list,
			academic_program_name,
			acad_prgm_studycode,
			download_files,
			pylogs_filepointer,
			f_failed_downloads
		)

		unknown_fields = list( dict.fromkeys(unknown_fields) )

		return return_info_dict, amount_downloads, amt_of_semesters_processed, unknown_fields

	def download_course_files(
		self,
		driver,
		course_number_URL,
		course_title,
		semester_list,
		academic_program_name,
		acad_prgm_studycode,
		download_files,
		pylogs_filepointer,
		f_failed_downloads
	):
		"""Download all files (for all semesters) corresponding to a course.

		Downloads are only available when being logged in. All (available) files
		are then downloaded into a temp folder and after downloading is finished,
		all files are moved to its final location.

		parameters:
		.) driver: webdriver instance object
		.) course_number_URL:	six digit course number, e.g., 103064. Used
								for folder creation (name).
		.) course_title:	name of the course (in german), used for folder creation
		.) semester_list{}:	contains a dict of semesters and corresponding
							downloadlinks, e.g., semester_list = {'2022W': '', '2021W':
							'https://tiss.tuwien.ac.at/education/course/documents.xhtml? \
							courseNr=103064&semester=2021W'}. Empty entries denote no
							available downloads.
		.) academic_program_name: The name of the academic program (e.g., 'Technische Physik')
		.) download_files:	bool which indicates whether files should be downloaded or not.
							If set to False, no downloading will happen.
		"""
		pylogs.write_to_logfile(pylogs_filepointer, 'starting downloading files')

		amount_downloads = 0

		if (not self.logged_in and download_files == True):
			#print("not logged in -> loggin in")
			self.tiss_login(driver)
		#else:
			#print("logged in")

		if self.logged_in == True and course_number_URL != "" and download_files == True:
			#print("course number: " + course_number_URL)
			#print("course title: " + course_title)
			#print("academic program name: " + academic_program_name)

			semester_list_key_dict = list(dict.fromkeys(semester_list))
			for i in range(len(semester_list_key_dict)):
				pylogs.write_to_logfile(pylogs_filepointer, 'processing: ' + semester_list_key_dict[i])
				materials_download_link = semester_list[semester_list_key_dict[i]]
				process_semester = semester_list[semester_list_key_dict[i]]

				if materials_download_link != "":
					#print("semester: " + semester_list_key_dict[i] + " -> " + "download url: " + materials_download_link)

					download_temp_path = self.download_path_root + self.download_path_temp
					download_move_path_courseNr = (self.download_path_root +
						academic_program_name + " - " + acad_prgm_studycode +
						"/" + course_number_URL + " " + course_title.replace("/", "-") + "/"
					)
					download_move_path_semester = download_move_path_courseNr + \
						semester_list_key_dict[i] + "/"

					# check if the folders exist
					check_folder = self.download_path_root + \
						academic_program_name + " - " + acad_prgm_studycode + "/"

					if not os.path.isdir(check_folder):
						#print("path " + check_folder + " does not exist - create folder")
						os.mkdir(check_folder)
					#else:
						#print("path " + check_folder + " exists")

					if not os.path.isdir(download_move_path_courseNr):
						#print("path " + download_move_path_courseNr + " does not exist - create folder")
						os.mkdir(download_move_path_courseNr)
					#else:
						#print("path " + download_move_path_courseNr + " exists")

					if not os.path.isdir(download_move_path_semester):
						#print("path " + download_move_path_semester + " does not exist - create folder")
						os.mkdir(download_move_path_semester)
					#else:
						#print("path " + download_move_path_semester + " exists")

					#double check, whether folder creation was successful
					if (not os.path.isdir(download_move_path_courseNr) or
						not os.path.isdir(download_move_path_semester)
					):
						#print("something went wrong with creating folders")
						warnings.warn("Error creating folders: " +
						download_move_path_courseNr + " or " + download_move_path_semester)
					else:
						# queue the files to download
						download_source_raw = self.fetch_page(driver, materials_download_link)
						i_amount_downloads = 0
						str_download_needle = 'onclick="'

						## wait for downloads to finish (and move them afterwards):
						# count the downloads in the *temp/-folder. When All downloads are
						# finished (no file with *.part ending), move them to the final location.
						download_first_iteration = True
						downloads_finished = False
						i_downloads = 0
						time_download_start = time.time()
						time_abort = 1000

						while download_source_raw.find(str_download_needle) != -1:
							download_source_raw = download_source_raw[download_source_raw.find(str_download_needle) + len(str_download_needle):]
							download_source_extract = download_source_raw[:download_source_raw.find('ui-widget"')]

							if (download_source_extract.find("Download all files as ZIP-File") != -1 or
								download_source_extract.find("Alle Dateien als ZIP-Datei herunterladen") != -1):
								break

							download_link = download_source_extract[:download_source_extract.find('"')]
							driver.execute_script(download_link)
							time.sleep(random.uniform(10.0, 15.0))

							i_amount_downloads += 1

						#print("Downloads queued: " + str(i_amount_downloads))

						# fetch all files in the /temp folder and check, whether the file ending
						# is ".part". All these files are being downloaded at the moment.
						# Check the file size difference after a certain amount of time.
						while downloads_finished == False:
							#print("iteration number: " + str(i_downloads))

							amt_finished_dwnload = 0
							amt_not_finished_dwnload = 0
							#max_filesize_found = 0

							i = 0

							for entry in os.scandir(download_temp_path):
								#print("~~~~~~~~~~~~~~~~~~")
								if entry.is_file():
									#print(str(i) + " -> " + entry.name)
									if entry.name[-5:] == ".part":
										#print("   path: " + download_temp_path + entry.name + " -> size: " + str(os.path.getsize(download_temp_path + entry.name)/1000 ))
										amt_not_finished_dwnload += 1
										#max_filesize_found = max(max_filesize_found, os.path.getsize(download_temp_path + entry.name))
									else:
										amt_finished_dwnload += 1
								#print("~~~~~~~~~~~~~~~~~~")
								#print("\n\n")
								i += 1

							if amt_not_finished_dwnload == 0:
								downloads_finished = True

							# download takes too long -> abort
							# TODO: if the download failed by any chance (browser download stall),
							# the file stops downloading and progress is made, the full time_abort is used.
							# Determine if all files are not downloading anymore (delta size check) and
							# abort/retry in that case.
							delta_t = time.time() - time_download_start
							if delta_t > time_abort:
								pylogs.write_to_logfile(f_failed_downloads, "time_abort_reached for: " +
									course_title + "; academic program: " + academic_program_name +
									"; semester: " + process_semester
								)
								break

							#print("max filesize: " + str(max_filesize_found/(1000*1000)))
							time.sleep(1)
							i_downloads += 1

						#print("amt_finished_dwnload: " + str(amt_finished_dwnload))
						#print("amt_not_finished_dwnload: " + str(amt_not_finished_dwnload))
						#print("downloads_finished: " + str(downloads_finished))
						#print("download time: " + str(delta_t))

						pylogs.write_to_logfile(pylogs_filepointer,
							'amt_finished_dwnload: ' + str(amt_finished_dwnload) +
							' ; amt_not_finished_dwnload: ' + str(amt_not_finished_dwnload) +
							' ; downloads_finished: ' + str(downloads_finished) +
							' ; time: ' + str(delta_t) +
							' ; downloads queued: ' + str(i_amount_downloads)
						)

						# in case all downloads are private (e.g. only available if enrolled),
						# remove the folder since it is only empty
						if i_amount_downloads == 0:
							if os.path.isdir(download_move_path_semester):
								os.rmdir(download_move_path_semester)

						# download successful -> move files to final location
						if downloads_finished == True and i_amount_downloads > 0 and amt_finished_dwnload > 0:
							if amt_finished_dwnload == i_amount_downloads:
								amount_downloads += i_amount_downloads
								for entry in os.scandir(download_temp_path):
									if entry.is_file():
										#print("move file: " + download_temp_path + entry.name + " into: " + download_move_path_semester + entry.name)
										if os.path.isdir(download_move_path_semester):
											os.rename(download_temp_path + entry.name, download_move_path_semester + entry.name)
										#else:
											#print("path: " + download_move_path_semester + " does not exists")
							else:
								pylogs.write_to_logfile(pylogs_filepointer,
									'Amount of queued files and amount of downloaded files differs!'
								)
								pylogs.write_to_logfile(f_failed_downloads,
									'Amount of queued files and amount of downloaded files differs: '+
									course_title + "; academic program: " + academic_program_name +
									"; semester: " + process_semester + "; downloads_finished: " +
									str(downloads_finished) + "; i_amount_downloads: " +
									str(i_amount_downloads) + "; amt_finished_dwnload: " +
									str(amt_finished_dwnload)
								)

						# clear temp folder of files in any way so that future downloads
						# will not fail (this folder should be empty at every starting download)
						i_temp_dwnld_clear = 0
						for entry in os.scandir(download_temp_path):
							if entry.is_file():
								i_temp_dwnld_clear += 1
								#print("del: " + entry.name)
								os.remove(download_temp_path + entry.name)

						#print("deleted " + str(i_temp_dwnld_clear) + " files remaining in /tmp")

						i_empty_check = 0
						for entry in os.scandir(download_temp_path):
							if entry.is_file():
								i_empty_check += 1

						if i_empty_check > 0:
							pylogs.write_to_logfile(pylogs_filepointer,
								"Error: folder " + download_temp_path + "not empty"
							)

		else:
			pylogs.write_to_logfile(pylogs_filepointer,
				"Not downloading files -> self.logged_in: " + str(self.logged_in) +
				"; course_number_URL: " + course_number_URL + "; download_files: " +
				str(download_files)
			)

		return amount_downloads

	def extract_course_info_lecturers(self, extract_info):
		cutstr1 = '<span>'
		cutstr2 = '</span>'

		extract_lecturer = []

		while extract_info.find(cutstr1) != -1:
			cutpos1 = extract_info.find(cutstr1)
			cutpos2 = extract_info.find(cutstr2)

			if cutpos2 > cutpos1:
				extract_lecturer.append(extract_info[cutpos1 + len(cutstr1):cutpos2])

			extract_info = extract_info[cutpos2 + len(cutstr2):]

		return extract_lecturer

	def extract_course_info_curricula(self, extract_info):
		curricula_return_list = []
		needle = ''

		if extract_info.find('semester=NEXT">') != -1:
			needle = 'semester=NEXT">'
		elif extract_info.find('semester=CURRENT">') != -1:
			needle = 'semester=CURRENT">'
		else:
			warnings.warn("Error processing curricula")

		if needle != "":
			while extract_info.find(needle) != -1:
				pos = extract_info.find(needle)
				extract_info = extract_info[pos + len(needle):]

				if extract_info.find(needle) != -1:
					pos1 = extract_info.find(needle)
					extract_info_temp = extract_info[:pos1]
				else:
					extract_info_temp = extract_info

				sempreconinfo_list = []
				study_code = extract_info_temp[:extract_info_temp.find('</a>')]
				curricula_return_list.append(study_code)

				# Semester,	Precon.	and Info
				for j in range(0, 3):
					needle2 = 'td role="gridcell">'
					pos2 = extract_info_temp.find(needle2)
					extract_info_temp = extract_info_temp[pos2 + len(needle2):]
					pos3 = extract_info_temp.find('</td>')
					extract_print = extract_info_temp[:pos3]
					# check steop condition
					steop_str1 = 'Studieneingangs- und Orientierungsphase'

					if j == 2 and (extract_print.find(steop_str1) != -1 or extract_print.find("STEOP") != -1):
						extract_print = "STEOP"

					#print(extract_print + "|", end = " ")
					sempreconinfo_list.append(extract_print)

				curricula_return_list.append(sempreconinfo_list)
		return curricula_return_list

	def close_driver(self, driver, pylogs_filepointer):
		'''Close the webdriver properly.'''
		pylogs.write_to_logfile(pylogs_filepointer, "closing driver")

		driver.close()	# close the current browser window
		driver.quit()	# calls driver.dispose which closes all the browser windows and ends the webdriver session properly
