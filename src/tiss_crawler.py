# -*- coding: utf-8 -*-
#!/usr/bin/python3

import numpy as np
import os
import sqlhandler
import sys
import time

from config import *
import crawl
import pylogs
import sqlhandler

"""
Two main logfiles:
a) queued_courses.txt: Contains links to single courses
https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=260300
https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=259630
https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=260668
.
.
.

b) academic_programs.txt: Academic program from which a) is being generated
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=37047|Architektur|Bachelorstudium Architektur
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=41934|Architektur|Masterstudium Architektur
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=42323|Architektur|Masterstudium Building Science and Environment
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59971|Architektur|Doktoratsstudium der Technischen Wissenschaften Architektur
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57488|Architektur|Katalog Freie Wahlfächer - Architektur
.
.
.

Possible cases:
1.) Neither a) nor b) exist at all (no file in /logs):
https://tiss.tuwien.ac.at/curriculum/studyCodes.xhtml will be
crawled and with that data b) is filled. In a loop, all entries
from b) will be processed and for each entry a file a) will be
generated and processed.

2.) Both a) and b) exist (a file with entries):
Same case as 2.) and the extracted data from b) will be appended
to the processing queue.

3.) b) exists but is empty (no entries) and a) exists (with data points):
Via the function process_courses() the courses are processed. This is
only an edge case since entries in b) are removed after all data in a)
is processed. If individual courses are to be processed, this case can
also apply.

Downloaded files in 1.) and 2.) are stored in the following structure:
.
└── downloads
    └── academic_program_name (e.g., 'Technische Physik')
       └── courseNr + Course name (e.g., '136019 Quantentheorie I')
          └── Semester (e.g., '2022W')
             ├── File #1
             ├── File #2
             ├── .
             ├── .
             └── .
          .
          .
          .
For the last case (3.)), the academic_program_name is not determinable
and the files are downloaded directly into the 'downloads' folder
"""

# stats variables
total_downloaded_files = 0
total_page_crawls = 0

def sql_insert_courses(return_info_dict, pylogs_filepointer, academic_program_name):
	"""Insert data into a SQL database
	"""
	pylogs.write_to_logfile(f_runtime_log, 'inserting into the database')

	# sql handler initialisation
	sqlhandlerObj = sqlhandler.SqlHandler()

	# unpack the information and insert it into the SQL db
	semester_dict_keys = list( return_info_dict.keys() )
	for key_semesters in semester_dict_keys:
		chosen_semester_dict = return_info_dict[key_semesters]

		# check if the data is already in the DB, which would be true
		# in case the program was interruped without finishing a course
		# completely
		page_fetch_lang = str(chosen_semester_dict.get("page_fetch_lang"))
		course_number = str(chosen_semester_dict.get("course number"))
		semester = str(chosen_semester_dict.get("semester"))

		sql_where = " WHERE page_fetch_lang = %s AND `course number` = %s AND semester = %s"
		sql_select = "SELECT * FROM "
		sql_values = (page_fetch_lang, course_number, semester)
		amount_of_datasets_in_DB = sqlhandlerObj.select_query(
			dbDatabase,
			academic_program_name,
			sql_values,
			sql_where,
			sql_select
		)

		if amount_of_datasets_in_DB > 0:
			pylogs.write_to_logfile(f_runtime_log,
				"Entry '" + page_fetch_lang + "|" + course_number +
				"|" + semester + "' is already in the DB"
			)
		else:
			# perform the insertion into the DB
			insertStatement = (
				"INSERT INTO " + academic_program_name + " (page_fetch_lang, \
				`course number`, `course title`, semester, type, sws, ECTS, \
				add_info, Merkmale, `Weitere Informationen`, \
				`Inhalt der Lehrveranstaltung`, Methoden, Prüfungsmodus, \
				Leistungsnachweis, LVA_Anmeldung, Literatur, Vorkenntnisse, \
				`Vorausgehende Lehrveranstaltungen`, `Vortragende Personen`, \
				Sprache, Institut, Gruppentermine, Prüfungen, Gruppen_Anmeldung, \
				`LVA Termine`, Curricula, `Ziele der Lehrveranstaltung`, Lernergebnisse) "
				"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, \
				%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
			)

			if chosen_semester_dict["Vortragende Personen"] != "":
				joined_lecturers = "|".join(chosen_semester_dict["Vortragende Personen"])
			else:
				joined_lecturers = "None"

			page_fetch_lang = str(chosen_semester_dict.get("page_fetch_lang"))
			course_number = str(chosen_semester_dict.get("course number"))
			course_title = str(chosen_semester_dict.get("course title"))
			semester = str(chosen_semester_dict.get("semester"))
			lecture_type = str(chosen_semester_dict.get("type"))
			sws = str(chosen_semester_dict.get("sws"))
			ects = str(chosen_semester_dict.get("ECTS"))
			add_info = str(chosen_semester_dict.get("add_info"))
			properties = str(chosen_semester_dict.get("Merkmale"))
			additional_information = str(chosen_semester_dict.get("Weitere Informationen0"))
			subject_of_course = str(chosen_semester_dict.get("Inhalt der Lehrveranstaltung"))
			methods = str(chosen_semester_dict.get("Methoden"))
			mode_of_examination = str(chosen_semester_dict.get("Prüfungsmodus"))
			examination_modalities = str(chosen_semester_dict.get("Leistungsnachweis"))
			course_registration = str(chosen_semester_dict.get("LVA-Anmeldung"))
			literature = str(chosen_semester_dict.get("Literatur"))
			previous_knowledge = str(chosen_semester_dict.get("Vorkenntnisse"))
			preceding_courses = str(chosen_semester_dict.get("Vorausgehende Lehrveranstaltungen"))
			lecturers = joined_lecturers
			language = str(chosen_semester_dict.get("Sprache"))
			institute = str(chosen_semester_dict.get("Institut"))
			group_dates = str(chosen_semester_dict.get("Gruppentermine"))
			exams = str(chosen_semester_dict.get("Prüfungen"))
			group_registration = str(chosen_semester_dict.get("Gruppen-Anmeldung"))
			course_dates = str(chosen_semester_dict.get("LVA Termine"))
			curricula = str(chosen_semester_dict.get("Curricula"))
			aim_of_the_course = str(chosen_semester_dict.get("Ziele der Lehrveranstaltung"))
			learning_outcomes = str(chosen_semester_dict.get("Lernergebnisse"))

			insertData = (page_fetch_lang, course_number, course_title, semester,
				lecture_type, sws, ects, add_info, properties, additional_information,
				subject_of_course, methods, mode_of_examination, examination_modalities,
				course_registration, literature, previous_knowledge, preceding_courses,
				lecturers, language, institute, group_dates, exams, group_registration,
				course_dates, curricula, aim_of_the_course, learning_outcomes)

			sqlhandlerObj.insert_into_table(dbDatabase, insertStatement, insertData, 0)

def process_courses(acad_course_list, academic_program_name, pylogs_filepointer, f_failed_downloads):
	"""Extract desired information for each course.

	This function takes a list of URLs pointing to courses
	corresponding to an academic program. This list may look similar like:
	https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=253G61
	https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=104590
	https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=264219
	https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=264232
	.
	.
	.
	
	Each URL is processed via 'driver_instance.extract_course_info()',
	which returns a dict containing the extracted data with the key
	being the semester and language (2022en, 2022de, etc.). This data
	is then inserted into a database for store.
	"""
	global total_downloaded_files
	global total_page_crawls

	pylogs.write_to_logfile(f_runtime_log, 'processing courses: ' + str(len(acad_course_list)) +
		'| academic program name: ' + academic_program_name)

	# create the SQL table
	sqlhandlerObj = sqlhandler.SqlHandler()

	create_info = " \
		`page_fetch_lang` char(2) NOT NULL, \
		`course number` char(7) NOT NULL, \
		`course title` tinytext NOT NULL, \
		`semester` char(5) NOT NULL, \
		`type` char(2) NOT NULL, \
		`sws` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL, \
		`ECTS` varchar(6) NOT NULL, \
		`add_info` tinytext NOT NULL, \
		`Merkmale` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL, \
		`Weitere Informationen` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL, \
		`Inhalt der Lehrveranstaltung` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL, \
		`Methoden` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL, \
		`Prüfungsmodus` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL, \
		`Leistungsnachweis` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL, \
		`LVA_Anmeldung` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL, \
		`Literatur` text NOT NULL, \
		`Vorkenntnisse` text NOT NULL, \
		`Vorausgehende Lehrveranstaltungen` text NOT NULL, \
		`Vortragende Personen` text NOT NULL, \
		`Sprache` text NOT NULL, \
		`Institut` text NOT NULL, \
		`Gruppentermine` text NOT NULL, \
		`Prüfungen` text NOT NULL, \
		`Gruppen_Anmeldung` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL, \
		`LVA Termine` text NOT NULL, \
		`Curricula` text NOT NULL, \
		`Ziele der Lehrveranstaltung` text NOT NULL, \
		`Lernergebnisse` text NOT NULL \
	"

	table_exists = sqlhandlerObj.create_table(dbDatabase, academic_program_name, create_info, 0)

	if table_exists == True:
		print("table '" + academic_program_name + "' already exists")
	else:
		print("table '" + academic_program_name + "' created")
		pylogs.write_to_logfile(f_runtime_log, 'SQL table "' + academic_program_name + '" created')

	# create folder structure where files page sourcefiles are stored
	if not os.path.isdir(root_dir + loggin_folder + academic_program_name):
		pylogs.write_to_logfile(f_runtime_log, 'folder "' + root_dir + loggin_folder +
			academic_program_name + '" does not exist -> creating')
		os.mkdir(root_dir + loggin_folder + academic_program_name)
	else:
		pylogs.write_to_logfile(f_runtime_log, 'folder "' + root_dir + loggin_folder +
			academic_program_name + '" exists')

	for process_course in acad_course_list[:]:
		# process the course
		return_info_dict, ret_dwnlds, ret_crawls, unknown_fields = driver_instance.extract_course_info(
			driver,
			process_course,
			academic_program_name,
			pylogs_filepointer,
			f_failed_downloads,
			True
		)

		# update amount of downloads and page crawls
		total_downloaded_files += ret_dwnlds
		total_page_crawls += ret_crawls

		# write info to logfiles
		pylogs.write_to_logfile(f_runtime_stats, "downloads: " + str(total_downloaded_files))
		pylogs.write_to_logfile(f_runtime_stats, "pages processed:  " + str(total_page_crawls))
		pylogs.write_to_logfile(f_runtime_log, 'amount of unkown fields: ' + str(len(unknown_fields)))
		for list_element in unknown_fields:
			pylogs.write_to_logfile(f_runtime_unknowns, list_element)

		# SQL insert the returned data
		sql_insert_courses(return_info_dict, pylogs_filepointer, academic_program_name)

		# remove the processed entry
		pylogs.write_to_logfile(f_runtime_log, process_course + ' processed -> remove entry')
		acad_course_list.remove(process_course)

		# update the logfile
		f = open(logging_folder + logging_queued_courses, "w")
		for i in range(len(acad_course_list)):
			f.write(acad_course_list[i] + "|" + academic_program_name + "\n")
		f.close()

# logfiles
f_runtime_log = pylogs.open_logfile(root_dir + loggin_folder + "runtime_log_" + pylogs.get_time())
f_runtime_stats = pylogs.open_logfile(root_dir + loggin_folder + "runtime_stats_" + pylogs.get_time())
f_runtime_unknowns = pylogs.open_logfile(root_dir + loggin_folder + "unkown_field_stats_" + pylogs.get_time())
f_failed_downloads = pylogs.open_logfile(root_dir + loggin_folder + "failed_download_stats_" + pylogs.get_time())

pylogs.write_to_logfile(f_runtime_log, "starting program")
pylogs.write_to_logfile(f_runtime_log, "runtime logfile for stats: " + os.path.basename(f_runtime_stats.name))

# set folders / files
logging_folder = "logs/"
logging_academic_programs = "academic_programs.txt"
logging_queued_courses = "queued_courses.txt"
pylogs.write_to_logfile(f_runtime_log, "logging_folder: " + logging_folder)
pylogs.write_to_logfile(f_runtime_log, "logging_academic_programs: " + logging_queued_courses)
pylogs.write_to_logfile(f_runtime_log, "logging_queued_courses: " + logging_queued_courses)

# initiate driver (instance)
pylogs.write_to_logfile(f_runtime_log, "initiating driver")
driver_instance = crawl.crawler(False, 800, 600, 10)
driver = driver_instance.init_driver()

# log in to get more semesters in the academic program
# which results in more courses found.
driver_instance.tiss_login(driver)

# check the state of eventual previous crawls
if not os.path.exists(logging_folder):
	raise Exception('Folder "' + logging_folder + '" does not exist')
else:
	print('Folder "' + logging_folder + '" exists')

# check (eventual queued) academic programs to crawl
if os.path.isfile(logging_folder + logging_academic_programs):
	# text file with (previous crawled) academic programs exists.
	# parse this file to continue from this point onwards.
	pylogs.write_to_logfile(f_runtime_log, 'file "' + logging_folder + logging_academic_programs + '" exists:')

	acad_program_list = []
	with open(logging_folder + logging_academic_programs) as file:
		for line in file:
			acad_program_list.append(line.rstrip())
			pylogs.write_to_logfile(f_runtime_log, line.rstrip())

else:
	# no file containing academic programs was found -> "start at zero". Fetch
	# all academic programs and add them to the list
	pylogs.write_to_logfile(f_runtime_log, 'file "' + logging_folder + logging_academic_programs + '" does not exist')

	# fetch all available academic programs
	academic_program_URL = "https://tiss.tuwien.ac.at/curriculum/studyCodes.xhtml"
	pylogs.write_to_logfile(f_runtime_log, 'fetching academic programs from ' + academic_program_URL + ':')

	# fetch this page always in the same language (download folder names!)
	if driver_instance.get_language(driver) != "de":
		driver_instance.switch_language(driver)

	acad_program_list = driver_instance.extract_academic_programs(
		driver,
		academic_program_URL
	)

	# write the information to the corresponding file
	f = open(logging_folder + logging_academic_programs, "w")
	for i in range(len(acad_program_list)):
		f.write(acad_program_list[i] + "\n")
		pylogs.write_to_logfile(f_runtime_log, acad_program_list[i])

	f.close()

# check (eventual queued) courses to crawl
acad_course_list = []
if os.path.isfile(logging_folder + logging_queued_courses):
	# text file with (previous crawled) academic programs exists.
	# parse this file to continue from this point onwards.
	pylogs.write_to_logfile(f_runtime_log, 'file "' + logging_folder + logging_queued_courses + '" exists:')

	with open(logging_folder + logging_queued_courses) as file:
		for line in file:
			#print(line.rstrip())
			process_acad_prgm_URL = line.rstrip().split('|')[0]
			process_acad_prgm_name = line.rstrip().split('|')[1]
			acad_course_list.append(process_acad_prgm_URL)
			pylogs.write_to_logfile(f_runtime_log, line.rstrip())
else:
	# no file containing academic programs was found -> "start at zero"
	pylogs.write_to_logfile(f_runtime_log, 'file "' + logging_folder + logging_queued_courses + '" does not exist')

pylogs.write_to_logfile(f_runtime_log, str(len(acad_course_list)) + " queued courses found")

# no academic programs in the logfile but courses, process these files
# first. This case should never catch.
if len(acad_course_list) > 0 and len(acad_program_list) == 0:
	process_courses(acad_course_list, process_acad_prgm_name, f_runtime_log, f_failed_downloads)

# continue/start crawling
for process_acad_prgm in acad_program_list[:]:
	#ttps://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57488|Architektur|Katalog Freie Wahlfächer - Architektur
	process_acad_prgm_URL = process_acad_prgm.split('|')[0]
	process_acad_prgm_name = process_acad_prgm.split('|')[1]
	process_acad_prgm_studycode = process_acad_prgm.split('|')[2]
	pylogs.write_to_logfile(f_runtime_log, "processing: " + process_acad_prgm_URL +
		" | " + process_acad_prgm_name + " | " + process_acad_prgm_studycode)

	# Take the URL of an academic program and extract all corresponding courses
	acad_course_list_fetch = driver_instance.extract_courses(driver, process_acad_prgm_URL)
	pylogs.write_to_logfile(f_runtime_log, '#queued academic courses (' +
		str(len(acad_course_list_fetch)) + "):")

	# append the fetched data to the processing list, remove duplicates
	acad_course_list.extend(acad_course_list_fetch)
	acad_course_list = list( dict.fromkeys(acad_course_list) )

	# write fetched courses into the logfile.
	f = open(logging_folder + logging_queued_courses, "w")
	for i in range(len(acad_course_list)):
		f.write(acad_course_list[i] + "|" + process_acad_prgm_name + "\n")
		pylogs.write_to_logfile(f_runtime_log, acad_course_list[i] + "|" + process_acad_prgm_name)
	f.close()

	# extract course information for the academic course´
	process_courses(acad_course_list, process_acad_prgm_name, f_runtime_log, f_failed_downloads)

	# remove the processed entry from acad_program_list
	acad_program_list.remove(process_acad_prgm)
	pylogs.write_to_logfile(f_runtime_log, 'program processed (remove): ' + process_acad_prgm)

	# update the logfile
	f = open(logging_folder + logging_academic_programs, "w")
	for i in range(len(acad_program_list)):
		f.write(acad_program_list[i] + "\n")
	f.close()

driver_instance.close_driver(driver, f_runtime_log)
pylogs.close_logfile(f_runtime_log)
pylogs.close_logfile(f_runtime_stats)
pylogs.close_logfile(f_runtime_unknowns)
pylogs.close_logfile(f_failed_downloads)
