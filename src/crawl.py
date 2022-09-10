# -*- coding: utf-8 -*-
#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from time import sleep
import warnings

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

	def extract_URLs(self, driver, URL, needle):
		"""Extract links to academic programs.

		Starting from an URL, this function extracts all
		URLs (hrefs) to all academic programs which serve
		as a starting point for further crawling. All found
		links are stored and returned via a list. When using
		the 'needle', only URLs containing this string will be
		returned from the haystack.
		"""
		fetched_page = self.fetch_page(driver, URL)

		elems = driver.find_elements_by_xpath("//a[@href]")
		found_elements = []

		for elem in elems:
			href_element = elem.get_attribute("href")
			# only select links (hrefs) to academic programs:
			if href_element.find(needle) != -1:
				found_elements.append(href_element)

		return found_elements

	def extract_courses(self, driver, URL):
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

		# selector element for year(semester) selection
		selector = Select(driver.find_element_by_name("j_id_2d:semesterSelect"))

		extracted_course_URLs = []

		# loop through all semesters and store all links to the courses
		for index in range(len(selector.options)):
			select = Select(driver.find_element_by_name("j_id_2d:semesterSelect"))
			select.select_by_index(index)
			sleep(2*self.sleeptime_fetchpage)

			# extract all links found
			elems = driver.find_elements_by_xpath("//a[@href]")
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
		extracted_course_URLs = list(dict.fromkeys(extracted_course_URLs)) 

		return extracted_course_URLs

	def extract_course_info(self, driver, URL):
		"""Process a single course and extract relevenat information.
		"""

		#TODO: split ger/eng version of this function(s)

		# dict containing all the extracted information
		extract_dict = {}

		# determine course number from the (given) URL
		needle = "courseNr="
		course_number = URL[URL.find(needle) + len(needle):]
		print("URL course number: " + course_number)

		print("processing: " + URL)
		course_raw_info = self.fetch_page(driver, URL)
		#f = open("src.txt", "r")
		#course_raw_info = f.read()
		#print(course_raw_info)

		# course number and course title
		needle1 = '<span class="light">'
		pos1 = course_raw_info.find(needle1)
		needle2 = "</span>"
		pos2 = course_raw_info.find(needle2)
		course_number = course_raw_info[pos1 + len(needle1):pos2].strip()
		print("course nmbr: |" +  course_number + "|")
		extract_dict["course number"] = course_number

		course_raw_info = course_raw_info[pos2 + len(needle2):]
		#print(course_raw_info)

		needle3 = "<"
		pos3 = course_raw_info.find(needle3)
		course_title = course_raw_info[:pos3].strip()
		print("course title: |" + course_title + "|")
		extract_dict["course title"] = course_title


		# quickinfo
		needle4 = '<div id="subHeader" class="clearfix">'
		pos4 = course_raw_info.find(needle4)
		needle5 = "</div>"
		pos5 = course_raw_info.find(needle5)
		quickinfo = course_raw_info[pos4 + len(needle4):pos5].strip()
		print("quickinfo: |" + quickinfo + "|")

		# "h2-extraction" - each information is separated by an h2 element
		needle6 = "<h2>"

		i = 0

		# certain sections may be present multiple times in the page. Therefore, count
		# how many times they are present and add the integer count to the dict index.
		count_entry_dict = {}
		count_entry_dict["Additional information"] = 0
		count_entry_dict["Weitere Informationen"] = 0

		while course_raw_info.find(needle6) != -1:
			pos6 = course_raw_info.find(needle6)
			course_raw_info = course_raw_info[pos6 + len(needle6):]

			print(str(i) + "########################################")

			if course_raw_info.find(needle6) != -1:
				pos7 = course_raw_info.find(needle6)
				extract_info = course_raw_info[:pos7]
			else:
				extract_info = course_raw_info

			#header
			header_needle = "</h2>"
			header_pos = extract_info.find(header_needle)
			header_titletext = extract_info[:header_pos]

			print(header_titletext + ":")

			extract_info = extract_info[header_pos + len(header_needle):]

			# html cleanup
			extract_info = extract_info.replace(' class="encode"', '')
			extract_info = extract_info.replace(' class="bulletList"', '')

			if header_titletext == "Properties" or header_titletext == "Merkmale":
				extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
				print(extract_info)
				extract_info = ""

			if header_titletext == "Learning outcomes" or header_titletext == "Lernergebnisse":
				extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
				extract_info = ""

			if header_titletext == "Subject of course" or header_titletext == "Inhalt der Lehrveranstaltung":
				extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
				extract_info = ""

			if header_titletext == "Teaching methods" or header_titletext == "Methoden":
				extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
				extract_info = ""

			if header_titletext == "Mode of examination" or header_titletext == "Prüfungsmodus":
				extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
				extract_info = ""

			add_info_flag = False

			if header_titletext == "Additional information" or header_titletext == "Weitere Informationen":
				add_info_flag = True
				past_entries = count_entry_dict["Weitere Informationen"]

				extract_dict[header_titletext + str(past_entries)] = extract_info.replace('\n', '').strip()
				extract_info = ""
				count_entry_dict["Weitere Informationen"] += 1

			if header_titletext == "Lecturers" or header_titletext == "Vortragende Personen":
				extract_dict[header_titletext] = self.extract_course_info_lecturers(extract_info)
				extract_info = ""

			if header_titletext == "Institute" or header_titletext == "Institut":
				needle = '<li><a href='
				pos1 = extract_info.find(needle)
				extract_info = extract_info[pos1 + len(needle):]
				extract_info = extract_info[extract_info.find('>') + 1:]
				extract_dict[header_titletext] = extract_info[:extract_info.find('<')].replace('\n', '').strip()
				extract_info = ""

			if header_titletext == "Course dates" or header_titletext == "LVA Termine":
				#TODO: extract this information
				course_coursedate_info = ""
				extract_info = ""

			if header_titletext == "Examination modalities" or header_titletext == "Leistungsnachweis":
				extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
				extract_info = ""

			if header_titletext == "Group dates" or header_titletext == "Gruppentermine":
				#TODO: extract this information
				course_exams_info = ""
				extract_info = ""

			if header_titletext == "Exams" or header_titletext == "Prüfungen":
				#TODO: extract this information
				course_exams_info = ""
				extract_info = ""

			if header_titletext == "Course registration" or header_titletext == "LVA-Anmeldung":
				extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
				extract_info = ""

			if header_titletext == "Group Registration" or header_titletext == "Gruppen-Anmeldung":
				#TODO: extract this information
				course_exams_info = ""
				extract_info = ""

			if header_titletext == "Curricula":
				extract_dict[header_titletext] = self.extract_course_info_curricula(extract_info)
				extract_info = ""

			if header_titletext == "Literature" or header_titletext == "Literatur":
				extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
				extract_info = ""

			if header_titletext == "Previous knowledge" or header_titletext == "Vorkenntnisse":
				extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
				extract_info = ""

			if header_titletext == "Preceding courses" or header_titletext == "Vorausgehende Lehrveranstaltungen":
				extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
				extract_info = ""

			if header_titletext == "Miscellaneous" or header_titletext == "Weitere Informationen" and add_info_flag == False:
				extract_dict[header_titletext] = extract_info.replace('\n', '').strip()
				extract_info = ""

			if header_titletext == "Sprache" or header_titletext == "Language":
				cut_str = '<input type="hidden" name='
				cut_pos = extract_info.find(cut_str)
				extract_dict[header_titletext] = extract_info[:cut_pos]
				extract_info = ""

			#if header_titletext != "Merkmale" and header_titletext != "Properties" and header_titletext != "Curricula" and header_titletext != "Literature" and header_titletext != "Literatur" and header_titletext != "Language" and header_titletext != "Sprache" and header_titletext != "Course registration" and header_titletext != "LVA-Anmeldung" and header_titletext != "Miscellaneous" and header_titletext != "Weitere Informationen" and header_titletext != "Learning outcomes" and header_titletext != "Lernergebnisse" and header_titletext != "Subject of course" and header_titletext != "Inhalt der Lehrveranstaltung" and header_titletext != "Teaching methods" and header_titletext != "Methoden" and header_titletext != "Mode of examination" and header_titletext != "Prüfungsmodus" and header_titletext != "Additional information" and header_titletext != "Weitere Informationen" and header_titletext != "Lecturers" and header_titletext != "Vortragende Personen" and header_titletext != "Institute" and header_titletext != "Institut" and header_titletext != "Examination modalities" and header_titletext != "Leistungsnachweis" and header_titletext != "LVA Termine" and header_titletext != "Course dates" and header_titletext != "Prüfungen" and header_titletext != "Exams" and header_titletext != "Group dates" and header_titletext != "Gruppentermine":

			if extract_info != "":
				warnings.warn("Error processing course description (unkown field)")

			i += 1

			if i > 100:
				break
		#print(extract_dict)
		print("\n\n")
		print(*extract_dict.items(), sep='\n\n')


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

		if extract_info.find('semester=NEXT">') != -1:
			needle = 'semester=NEXT">'
		elif extract_info.find('semester=CURRENT">') != -1:
			needle = 'semester=CURRENT">'
		else:
			needle = ''
			warnings.warn("Error processing curricula")

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

				if j == 2 and extract_print.find(steop_str1) != -1:
					extract_print = "STEOP"
				#print(extract_print + "|", end = " ")
				sempreconinfo_list.append(extract_print)

			curricula_return_list.append(sempreconinfo_list)
		return curricula_return_list

	def close_driver(self, driver):
		'''Close the webdriver properly.'''
		print ('closing driver')

		driver.close()	# close the current browser window
		driver.quit()	# calls driver.dispose which closes all the browser windows and ends the webdriver session properly
