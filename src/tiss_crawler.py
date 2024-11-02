# -*- coding: utf-8 -*-
#!/usr/bin/python3

import numpy as np
import os
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

# False -> each INSERT statement is directly inserted into the DB (slower)
# True -> the insertion statements are written to a file on the disk
writeInsertToFile = True

# insertion override: if this variable is _not_ set to "", the name of the table
# into which the data is being inserted is defined by this variable (and not the
# academic program name)
insertIntoTableName = "crawl2024W"

# if enabled (fetchSingleSem != False), only the semester defined by the variable
# will be crawled. The given value must be equivalent to the value in the option/
# dropdown semester select, e.g., 2021W, 2017S, etc. The idea of this variable is,
# to only fetch course information about courses for this (single) semester. Database
# integrity testing (whether the course is already in the DB) will be skipped since
# this data is used to add data to the DB (no "initial crawl").
fetchSingleSem = "2024W"

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

		"""
		# This should be redundant since existance in the DB is checked beforehand (see -> course_already_in_DB)




		# when writing to a files directly, skip the query if the course is already in the DB
		if writeInsertToFile == False:
			# search through all tables if the course is already in the DB
			course_already_in_DB = False
			all_sql_tables = sqlhandlerObj.fetch_all_tables(dbDatabase)

			for query_table in all_sql_tables:
				sql_where = " WHERE page_fetch_lang = %s AND `course number` = %s AND semester = %s"
				sql_select = "SELECT * FROM "
				sql_values = (page_fetch_lang, course_number, semester)
				amount_of_datasets_in_DB = sqlhandlerObj.select_query(
					dbDatabase,
					query_table,
					sql_values,
					sql_where,
					sql_select
				)

				if len(amount_of_datasets_in_DB) > 0:
					pylogs.write_to_logfile(f_runtime_log,
						"Entry '" + page_fetch_lang + "|" + course_number +
						"|" + semester + "' is already in the DB"
					)
					course_already_in_DB = True
					break
		else:
			course_already_in_DB = False
		"""
		course_already_in_DB = False

		if course_already_in_DB == False:
			# override table name in which the data is to be inserted
			if insertIntoTableName != "":
				academic_program_name = insertIntoTableName

			# perform the insertion into the DB
			insertStatement = (
				"INSERT INTO `" + academic_program_name + "` (page_fetch_lang, \
				`course number`, `course title`, semester, type, sws, ECTS, \
				add_info, Merkmale, `Weitere Informationen`, \
				`Inhalt der Lehrveranstaltung`, Methoden, Prüfungsmodus, \
				Leistungsnachweis, LVA_Anmeldung, Literatur, Vorkenntnisse, \
				`Vorausgehende Lehrveranstaltungen`, `Vortragende Personen`, \
				Sprache, Institut, Gruppentermine, Prüfungen, Gruppen_Anmeldung, \
				`LVA Termine`, Curricula, `Ziele der Lehrveranstaltung`, Lernergebnisse) "
			)

			# additional string when inserting directly into the sql DB
			connectorAddStr = "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, \
				%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

			try:
				if chosen_semester_dict["Vortragende Personen"] != "":
					joined_lecturers = "|".join(chosen_semester_dict["Vortragende Personen"])
				else:
					joined_lecturers = "None"
			except KeyError:
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

			# executing each SQL insertion statement sequentially takes a significant amount
			# of time. Either do this or write the statements into a file (and process them
			# in another way, e.g., on the server)
			if writeInsertToFile == False:
				sqlhandlerObj.insert_into_table(dbDatabase, insertStatement + connectorAddStr, insertData, 1)
			else:
				pylogs.write_to_logfile(f_insertionStatements, insertStatement + " VALUES " + str(insertData) + ";\n", True, False)

def process_courses(
	acad_course_list,
	academic_program_name,
	acad_prgm_studycode,
	pylogs_filepointer,
	f_failed_downloads
):
	"""Extract desired information for each course.

	This function takes a list of URLs pointing to courses
	corresponding to an academic program. This list may look like:
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
		'| academic program name: ' + academic_program_name + ' | academic program studycode: ' +
		acad_prgm_studycode
	)

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

	"""
	get a list of all tables in the database and extract all courses
	in these databases. This list will be used to determine, whether
	a course is already in the database (since the study programs
	share courses). This list is updated during runtime (successfully
	processed courses are added to the list).

	stored already processed courses in this dict:
	processed_courses_list = {
		"physics": [c1, c2, c3, ...],
		"electrical engineering": [c1000, c1001, c1002, ...],
		.
		.
		.
	}
	with c1, c2, c3 ... being courses for physics
	and c1000, c1001, c1002, ... belonging to electrical engineering
	"""
	processed_courses_list = []

	sqlhandlerObj2 = sqlhandler.SqlHandler()

	# fetch all tables from the database
	all_sql_tables = sqlhandlerObj2.fetch_all_tables(dbDatabase)

	# populate the list of courses (select all course numbers
	# from a tables
	for query_table in all_sql_tables:
		print(query_table)
		sql_where = ""
		sql_select = "SELECT `course number` FROM "
		sql_values = ( )
		result = sqlhandlerObj2.select_query(
			dbDatabase,
			query_table,
			sql_values,
			sql_where,
			sql_select
		)

		# convert the set to a list
		result_list = []

		for x in result:
			result_list.append(x[0])

		#remove duplicates
		result_list_unique = list(set(result_list))

		append_dict = {query_table: result_list_unique}
		processed_courses_list.append(dict(append_dict))

	# work the process queue
	for process_course in acad_course_list[:]:
		# check if the course is already in the DB, if not -> process this course.
		# If it is found in the DB, do not process the course and just remove the
		# entry from the list.
		# TODO: if the (batch)insertion fails, data will be missing because insertion
		#		  is skipped in this case!
		temp_course_number = process_course[process_course.find('=') + 1:]
		process_course_number = temp_course_number[:3] + "." + temp_course_number [3:]

		course_already_in_DB = False
		found_in_table = ""

		# skip DB check (see comment at variable 'fetchSingleSem' definition)
		if fetchSingleSem == False:
			"""
			loop through all fetched courses and determine whether the current (to be processed)
			course is in any table. This data does not need to be updated since after one passthrough
			of an academic program, the list is read again and if the program is restarted the list
			is re-read also.
			"""
			for _ in processed_courses_list:
				for key in _.keys():
					if process_course_number in _[key]:
						found_in_table = key
						course_already_in_DB = True
						pylogs.write_to_logfile(f_runtime_log, "course: " +
							process_course_number + " found in DB(" + str(found_in_table) + ") -> skip"
						)
						break

			# TODO:	implement this check in crawl.py instead of making another
			#			call to check_course_exists() here
			#process_course_number = temp_course_number[:3] + "." + temp_course_number [3:]

			check_url = "https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=" + temp_course_number
			course_exists = driver_instance.check_course_exists(driver, check_url)
		# override the check if the course exists (only used for bruteforce data, which
		# is not always consistent (reports courses for existing despite the course not existing
		else:
			course_exists = True

		if course_already_in_DB == False and course_exists:
			# process the course
			return_info_dict, \
			ret_dwnlds, \
			ret_crawls, \
			unknown_fields = driver_instance.extract_course_info(
				driver,
				process_course,
				academic_program_name,
				acad_prgm_studycode,
				pylogs_filepointer,
				f_failed_downloads,
				fetchSingleSem,
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

# global logfile
f_runtime_log_global = pylogs.open_logfile(root_dir + logging_folder + "runtime_global_log_" + pylogs.get_time())

pylogs.write_to_logfile(f_runtime_log_global, "starting program")

# set folders / files
logging_academic_programs = "academic_programs.txt"
logging_queued_courses = "queued_courses.txt"
pylogs.write_to_logfile(f_runtime_log_global, "logging_folder: " + logging_folder)
pylogs.write_to_logfile(f_runtime_log_global, "logging_academic_programs: " + logging_queued_courses)
pylogs.write_to_logfile(f_runtime_log_global, "logging_queued_courses: " + logging_queued_courses)

# initiate driver (instance)
crawl_delay = 5
pylogs.write_to_logfile(f_runtime_log_global, "initiating driver")
pylogs.write_to_logfile(f_runtime_log_global, "crawl_delay: " + str(crawl_delay))
pylogs.write_to_logfile(f_runtime_log_global, "fetchSingleSem: " + str(fetchSingleSem))

driver_instance = crawl.crawler(False, 800, 600, crawl_delay)
driver = driver_instance.init_driver()

# set the timeout for page loads (in units of seconds)
driver.set_page_load_timeout(120)

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
	pylogs.write_to_logfile(f_runtime_log_global, 'file "' + logging_folder + logging_academic_programs + '" exists:')

	acad_program_list = []
	with open(logging_folder + logging_academic_programs) as file:
		for line in file:
			acad_program_list.append(line.rstrip())
			pylogs.write_to_logfile(f_runtime_log_global, line.rstrip())
else:
	# no file containing academic programs was found -> "start at zero". Fetch
	# all academic programs and add them to the list
	pylogs.write_to_logfile(f_runtime_log_global, 'file "' + logging_folder + logging_academic_programs + '" does not exist')

	# fetch all available academic programs
	academic_program_URL = "https://tiss.tuwien.ac.at/curriculum/studyCodes.xhtml"
	pylogs.write_to_logfile(f_runtime_log_global, 'fetching academic programs from ' + academic_program_URL + ':')

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
		pylogs.write_to_logfile(f_runtime_log_global, acad_program_list[i])

	f.close()

# check (eventual queued) courses to crawl
acad_course_list = []
if os.path.isfile(logging_folder + logging_queued_courses):
	# text file with (previous crawled) academic programs exists.
	# parse this file to continue from this point onwards.
	pylogs.write_to_logfile(f_runtime_log_global, 'file "' + logging_folder + logging_queued_courses + '" exists:')

	with open(logging_folder + logging_queued_courses) as file:
		for line in file:
			#print(line.rstrip())
			process_acad_prgm_URL = line.rstrip().split('|')[0]
			process_acad_prgm_name = line.rstrip().split('|')[1]
			acad_course_list.append(process_acad_prgm_URL)
			pylogs.write_to_logfile(f_runtime_log_global, line.rstrip(), False)
else:
	# no file containing academic programs was found -> "start at zero"
	pylogs.write_to_logfile(f_runtime_log_global, 'file "' + logging_folder + logging_queued_courses + '" does not exist')

pylogs.write_to_logfile(f_runtime_log_global, str(len(acad_course_list)) + " queued courses found")

# no academic programs in the logfile but courses, process these files
# first. This case should never catch since an academic program gets only
# removed if the course list is empty.
if len(acad_course_list) > 0 and len(acad_program_list) == 0:
	print("academic list empty but queued courses not!")
	# override the academic program (set manually)
	acad_program_list = [" |NoCurricula|NoCurricula"]
	#acad_program_list.append(" |NoCurricula|NoCurricula");
	#process_courses(acad_course_list, process_acad_prgm_name, f_runtime_log, f_failed_downloads)
	#sys.exit()

# continue/start crawling
for process_acad_prgm in acad_program_list[:]:
	#ttps://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57488|Architektur|Katalog Freie Wahlfächer - Architektur
	process_acad_prgm_URL = process_acad_prgm.split('|')[0]
	process_acad_prgm_name = process_acad_prgm.split('|')[1]
	process_acad_prgm_studycode = process_acad_prgm.split('|')[2].replace("/", "-")

	# store each files corresponding to an academic program in separate folders (src files and logs)
	acad_program_path = (root_dir + logging_folder + process_acad_prgm_name +
		' - ' + process_acad_prgm_studycode
	)
	acad_program_path_logs = acad_program_path + " (logs)"
	pylogs.write_to_logfile(f_runtime_log_global, 'acad_program_path: ' + acad_program_path)
	pylogs.write_to_logfile(f_runtime_log_global, 'acad_program_path_logs: ' + acad_program_path_logs)

	# check if folders (page sources; logs) exist and if not, create them
	if not os.path.isdir(acad_program_path):
		pylogs.write_to_logfile(f_runtime_log_global, 'folder "' + acad_program_path +
			'" does not exist -> creating'
		)
		os.mkdir(acad_program_path)
	else:
		pylogs.write_to_logfile(f_runtime_log_global, 'folder "' + acad_program_path +
			'" exists'
		)

	if not os.path.isdir(acad_program_path_logs):
		pylogs.write_to_logfile(f_runtime_log_global, 'folder "' + acad_program_path_logs +
			'" does not exist -> creating'
		)
		os.mkdir(acad_program_path_logs)
	else:
		pylogs.write_to_logfile(f_runtime_log_global, 'folder "' + acad_program_path_logs +
			'" exists'
		)

	# create log files for the crawl of this academic program
	f_runtime_log = pylogs.open_logfile(acad_program_path_logs +
		"/runtime_log_" + pylogs.get_time())
	f_runtime_stats = pylogs.open_logfile(acad_program_path_logs +
		"/runtime_stats_" + pylogs.get_time())
	f_runtime_unknowns = pylogs.open_logfile(acad_program_path_logs +
		"/unkown_field_stats_" + pylogs.get_time())
	f_failed_downloads = pylogs.open_logfile(acad_program_path_logs +
		"/failed_download_stats_" + pylogs.get_time())

	# save insertion statement directly into logs folder
	f_insertionStatements = pylogs.open_logfile(root_dir + logging_folder +
		"/insertion_statements" + pylogs.get_time())

	pylogs.write_to_logfile(f_runtime_log_global, "f_runtime_log: " +
		os.path.basename(f_runtime_log.name))
	pylogs.write_to_logfile(f_runtime_log_global, "f_runtime_unknowns: " +
		os.path.basename(f_runtime_unknowns.name))
	pylogs.write_to_logfile(f_runtime_log_global, "f_failed_downloads: " +
		os.path.basename(f_failed_downloads.name))

	pylogs.write_to_logfile(f_runtime_log, "processing: " + process_acad_prgm_URL +
		" | " + process_acad_prgm_name + " | " + process_acad_prgm_studycode)

	# process_acad_prgm_URL == " " for queued courses but no queued academic programs
	if process_acad_prgm_URL != " ":
		# Take the URL of an academic program and extract all corresponding courses
		acad_course_list_fetch = driver_instance.extract_courses(driver, process_acad_prgm_URL, f_runtime_log, fetchSingleSem)
		pylogs.write_to_logfile(f_runtime_log, '#queued academic courses (' +
			str(len(acad_course_list_fetch)) + "):")

		# append the fetched data to the processing list, remove duplicates
		acad_course_list.extend(acad_course_list_fetch)

	acad_course_list = list( dict.fromkeys(acad_course_list) )

	# write fetched courses into the logfile.
	f = open(logging_folder + logging_queued_courses, "w")
	for i in range(len(acad_course_list)):
		f.write(acad_course_list[i] + "|" + process_acad_prgm_name + "\n")
		pylogs.write_to_logfile(f_runtime_log, acad_course_list[i] + "|" + process_acad_prgm_name, False)
	f.close()

	# extract course information for the academic course
	process_courses(
		acad_course_list,
		process_acad_prgm_name,
		process_acad_prgm_studycode,
		f_runtime_log,
		f_failed_downloads
	)

	# remove the processed entry from acad_program_list
	acad_program_list.remove(process_acad_prgm)
	pylogs.write_to_logfile(f_runtime_log_global, 'program processed (remove): ' + process_acad_prgm)

	total_downloaded_files = 0
	total_page_crawls = 0

	# update the logfile
	f = open(logging_folder + logging_academic_programs, "w")
	for i in range(len(acad_program_list)):
		f.write(acad_program_list[i] + "\n")
	f.close()

	pylogs.close_logfile(f_runtime_log)
	pylogs.close_logfile(f_runtime_stats)
	pylogs.close_logfile(f_runtime_unknowns)
	pylogs.close_logfile(f_failed_downloads)

driver_instance.close_driver(driver, f_runtime_log_global)
pylogs.close_logfile(f_runtime_log_global)
