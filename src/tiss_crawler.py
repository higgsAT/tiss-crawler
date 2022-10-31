# -*- coding: utf-8 -*-
#!/usr/bin/python3

import os
import sqlhandler
import time
import pylogs
import sys

from config import *
import crawl
import pylogs

f_runtime = pylogs.open_logfile(root_dir + loggin_folder + "runtime_log_" + pylogs.get_time())
pylogs.write_to_logfile(f_runtime, "starting program")
#pylogs.dump_to_log(root_dir + loggin_folder + "dump_test", "this is a dump test")

#pylogs.dump_to_log(root_dir + loggin_folder + pylogs.get_time() + "aa" + '.txt', "starting program")

#sys.exit()

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

def process_courses(acad_course_list, academic_program_name, pylogs_filepointer):
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
	pylogs.write_to_logfile(f_runtime, 'processing courses: ' + str(len(acad_course_list)) +
		'| academic program name: ' + academic_program_name)

	# create folder structure where files page sourcefiles are stored
	if not os.path.isdir(root_dir + loggin_folder + academic_program_name):
		pylogs.write_to_logfile(f_runtime, 'folder "' + root_dir + loggin_folder +
			academic_program_name + '" does not exist -> creating')
		os.mkdir(root_dir + loggin_folder + academic_program_name)
	else:
		pylogs.write_to_logfile(f_runtime, 'folder "' + root_dir + loggin_folder +
			academic_program_name + '" exists')

	for process_course in acad_course_list[:]:
		# process the course
		return_info_dict = driver_instance.extract_course_info(
			driver,
			process_course,
			academic_program_name,
			pylogs_filepointer,
			True
		)

		# SQL insert the returned data
		# TODO
		time.sleep(1.25)

		# remove the processed entry
		pylogs.write_to_logfile(f_runtime, process_course + ' processed -> remove entry')
		acad_course_list.remove(process_course)
		#print(acad_course_list)

		# update the logfile
		f = open(logging_folder + logging_queued_courses, "w")
		for i in range(len(acad_course_list)):
			f.write(acad_course_list[i] + "\n")
			f.write(acad_course_list[i] + "|" + academic_program_name + "\n")
		f.close()

# set folders / files
logging_folder = "logs/"
logging_academic_programs = "academic_programs.txt"
logging_queued_courses = "queued_courses.txt"
pylogs.write_to_logfile(f_runtime, "logging_folder: " + logging_folder)
pylogs.write_to_logfile(f_runtime, "logging_academic_programs: " + logging_queued_courses)
pylogs.write_to_logfile(f_runtime, "logging_queued_courses: " + logging_queued_courses)

# initiate driver (instance)
pylogs.write_to_logfile(f_runtime, "initiating driver")
driver_instance = crawl.crawler(False, 800, 600, 10)
driver = driver_instance.init_driver()

# log in to get more semesters in the academic program
# which results in more courses found.
#driver_instance.tiss_login(driver)

# check the state of eventual previous crawls
if not os.path.exists(logging_folder):
	raise Exception('Folder "' + logging_folder + '" does not exist')
else:
	print('Folder "' + logging_folder + '" exists')

# check (eventual queued) academic programs to crawl
if os.path.isfile(logging_folder + logging_academic_programs):
	# text file with (previous crawled) academic programs exists.
	# parse this file to continue from this point onwards.
	pylogs.write_to_logfile(f_runtime, 'file "' + logging_folder + logging_academic_programs + '" exists:')

	acad_program_list = []
	with open(logging_folder + logging_academic_programs) as file:
		for line in file:
			acad_program_list.append(line.rstrip())
			pylogs.write_to_logfile(f_runtime, line.rstrip())

else:
	# no file containing academic programs was found -> "start at zero". Fetch
	# all academic programs and add them to the list
	pylogs.write_to_logfile(f_runtime, 'file "' + logging_folder + logging_academic_programs + '" does not exist')

	# fetch all available academic programs
	academic_program_URL = "https://tiss.tuwien.ac.at/curriculum/studyCodes.xhtml"
	pylogs.write_to_logfile(f_runtime, 'fetching academic programs from ' + academic_program_URL + ':')

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
		pylogs.write_to_logfile(f_runtime, acad_program_list[i])

	f.close()

# check (eventual queued) courses to crawl
acad_course_list = []
if os.path.isfile(logging_folder + logging_queued_courses):
	# text file with (previous crawled) academic programs exists.
	# parse this file to continue from this point onwards.
	pylogs.write_to_logfile(f_runtime, 'file "' + logging_folder + logging_queued_courses + '" exists:')

	with open(logging_folder + logging_queued_courses) as file:
		for line in file:
			#print(line.rstrip())
			process_acad_prgm_URL = line.rstrip().split('|')[0]
			process_acad_prgm_name = line.rstrip().split('|')[1]
			acad_course_list.append(process_acad_prgm_URL)
			pylogs.write_to_logfile(f_runtime, line.rstrip())
else:
	# no file containing academic programs was found -> "start at zero"
	pylogs.write_to_logfile(f_runtime, 'file "' + logging_folder + logging_queued_courses + '" does not exist')

pylogs.write_to_logfile(f_runtime, str(len(acad_course_list)) + " queued courses found")

# no academic programs in the logfile but courses, process these files
# first. This case should never catch.
if len(acad_course_list) > 0 and len(acad_program_list) == 0:
	process_courses(acad_course_list, process_acad_prgm_name, f_runtime)

# continue/start crawling
for process_acad_prgm in acad_program_list[:]:
	#ttps://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57488|Architektur|Katalog Freie Wahlfächer - Architektur
	process_acad_prgm_URL = process_acad_prgm.split('|')[0]
	process_acad_prgm_name = process_acad_prgm.split('|')[1]
	process_acad_prgm_studycode = process_acad_prgm.split('|')[2]
	pylogs.write_to_logfile(f_runtime, "processing: " + process_acad_prgm_URL +
		" | " + process_acad_prgm_name + " | " + process_acad_prgm_studycode)

	# Take the URL of an academic program and extract all corresponding courses
	acad_course_list_fetch = driver_instance.extract_courses(driver, process_acad_prgm_URL)
	pylogs.write_to_logfile(f_runtime, '#queued academic courses (' +
		str(len(acad_course_list_fetch)) + "):")

	# append the fetched data to the processing list, remove duplicates
	acad_course_list.extend(acad_course_list_fetch)
	acad_course_list = list( dict.fromkeys(acad_course_list) )

	# write fetched courses into the logfile.
	f = open(logging_folder + logging_queued_courses, "w")
	for i in range(len(acad_course_list)):
		f.write(acad_course_list[i] + "|" + process_acad_prgm_name + "\n")
		pylogs.write_to_logfile(f_runtime, acad_course_list[i] + "|" + process_acad_prgm_name)
	f.close()

	# extract course information for the academic course´
	process_courses(acad_course_list, process_acad_prgm_name, f_runtime)

	# remove the processed entry from acad_program_list
	acad_program_list.remove(process_acad_prgm)
	pylogs.write_to_logfile(f_runtime, 'program processed (remove): ' + process_acad_prgm)

	# update the logfile
	f = open(logging_folder + logging_academic_programs, "w")
	for i in range(len(acad_program_list)):
		f.write(acad_program_list[i] + "\n")
	f.close()

pylogs.write_to_logfile(f_runtime, "closing " + f_runtime)
pylogs.close_logfile(f_runtime)
pylogs.write_to_logfile(f_runtime, "closing driver")
driver_instance.close_driver(driver)
