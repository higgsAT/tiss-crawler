# -*- coding: utf-8 -*-
#!/usr/bin/python3

import os
import sqlhandler
import time

import crawl
import pylogs

"""
Two main logfiles:
a) queued_courses.txt: Contains links to single courses
https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=260300
https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=259630
https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=260668
.
.
.

b) academic_programs.txt: Academic program from which a) is being generate
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=40337|UF Mathematik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=40406|UF Darstellende Geometrie
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=40505|UF Physik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=40766|UF Chemie
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
"""

def process_courses(acad_course_list):
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
	# work the courses-queue list
	print("PROCESS COURSES: " + str(len(acad_course_list)))
	for process_course in acad_course_list[:]:
		# process the course
		"""
		download_files = True
		return_info_dict = driver_instance.extract_course_info(
			driver,
			process_course,
			download_files
		)
		"""

		# SQL insert the returned data
		# TODO
		time.sleep(1.25)

		# remove the processed entry
		acad_course_list.remove(process_course)
		#print(acad_course_list)

		# update the logfile
		f = open(logging_folder + logging_queued_courses, "w")
		for i in range(len(acad_course_list)):
			f.write(acad_course_list[i] + "\n")
		f.close()


# set folders / files
logging_folder = "logs/"
logging_academic_programs = "academic_programs.txt"
logging_queued_courses = "queued_courses.txt"

# initiate driver (instance)
driver_instance = crawl.crawler(False, 800, 600, 5)
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
	print('file "' + logging_folder + logging_academic_programs + '" exists')

	acad_program_list = []
	with open(logging_folder + logging_academic_programs) as file:
		for line in file:
			acad_program_list.append(line.rstrip())
else:
	# no file containing academic programs was found -> "start at zero"
	print('file "' + logging_folder + logging_academic_programs + '" does not exist')

	# fetch all available academic programs
	academic_program_URL = "https://tiss.tuwien.ac.at/curriculum/studyCodes.xhtml"
	acad_program_list = driver_instance.extract_academic_programs(
		driver,
		academic_program_URL,
		"key"
	)

	# write the information to the corresponding file
	f = open(logging_folder + logging_academic_programs, "w")
	for i in range(len(acad_program_list)):
		f.write(acad_program_list[i] + "\n")
	f.close()

# check (eventual queued) courses to crawl
acad_course_list = []
if os.path.isfile(logging_folder + logging_queued_courses):
	# text file with (previous crawled) academic programs exists.
	# parse this file to continue from this point onwards.
	print('file "' + logging_folder + logging_queued_courses + '" exists')

	with open(logging_folder + logging_queued_courses) as file:
		for line in file:
			acad_course_list.append(line.rstrip())
else:
	# no file containing academic programs was found -> "start at zero"
	print('file "' + logging_folder + logging_queued_courses + '" does not exist')

print(str(len(acad_course_list)) + " queued courses found")

# no academic programs in the logfile but courses
if len(acad_course_list) > 0 and len(acad_program_list) == 0:
	process_courses(acad_course_list)

# continue/start crawling
for process_acad_prgm in acad_program_list[:]:
	process_acad_prgm_URL = process_acad_prgm.split('|')[0]
	process_acad_prgm_name = process_acad_prgm.split('|')[1]
	print("processing: " + process_acad_prgm_URL + " | " + process_acad_prgm_name)

	# Take the URL of an academic program and extract all corresponding courses
	acad_course_list_fetch = driver_instance.extract_courses(driver, process_acad_prgm_URL)

	# append the fetched data to the processing list
	acad_course_list.extend(acad_course_list_fetch)

	# write extracted courses into the logfile.
	f = open(logging_folder + logging_queued_courses, "w")
	for i in range(len(acad_course_list)):
		f.write(acad_course_list[i] + "\n")
	f.close()

	# extract course information for the academic course
	process_courses(acad_course_list)

	# remove the processed entry from acad_program_list
	acad_program_list.remove(process_acad_prgm)

	# update the logfile
	f = open(logging_folder + logging_academic_programs, "w")
	for i in range(len(acad_program_list)):
		f.write(acad_program_list[i] + "\n")
	f.close()

driver_instance.close_driver(driver)
