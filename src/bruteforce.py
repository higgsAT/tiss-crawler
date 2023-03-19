# -*- coding: utf-8 -*-
#!/usr/bin/python3

import numpy as np
import os
import sys
import time

from config import *
import crawl
import sqlhandler

# https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=017A02|Universitätslehrgang

def fetch_processed_courses():
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

	Argument(s):
	none

	Return(s):
	o)	processed_courses_list:	list (containing dicts) with the fetched
										(processed) courses from the database
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

	return processed_courses_list


def check_course_processed(process_course_number):
	"""
	loop through all fetched courses and determine whether the current (to be processed)
	course is in any table. This data does not need to be updated since after one passthrough
	of an academic program, the list is read again and if the program is restarted the list
	is re-read also.

	Example usage:
	check_course_processed("101.666")
	check_course_processed("302.666")


	Argument(s):
	o)	process_course_number:	Course number to be checked if it was already
										processed (e.g., "101.666", "101.667", etc.)

	Return(s):
	o)	course_already_in_DB:	True/False whether the course number is in
										the list.
	o) found_in_table:	table in the database in which the course number
								was found
	"""

	course_already_in_DB = False
	found_in_table = ''

	for _ in processed_courses_list:
		for key in _.keys():
			if process_course_number in _[key]:
				found_in_table = key
				course_already_in_DB = True
				break

	return course_already_in_DB, found_in_table

def write_to_file(filepointer, msg):
	filepointer.write(msg + "\n")

	filepointer.flush()
	os.fsync(filepointer)

# create a list (of dicts) containing the processed courses
processed_courses_list = fetch_processed_courses()

# variable declaration / (web)driver initation
crawl_delay = 5

# check course numbers (brute force) in the range between these two variables
check_course_start = 431752
check_course_end = 1000000

driver_instance = crawl.crawler(False, 800, 600, crawl_delay)
driver = driver_instance.init_driver()

# open (log)files
f_courses_to_process = open("logs/courses_to_process.txt", "a")
f_invalid_courses = open("logs/courses_invalid.txt", "a")
f_courses_in_DB = open("logs/courses_already_in_DB.txt", "a")

for _ in range(check_course_start, check_course_end):
	# generate course number (zerofill)
	check_course_number = str(_).zfill(6)

	print ( "checking: " + str(check_course_number) )

	# check if the course has already been processed
	check_course_db = check_course_number[:3] + "." + check_course_number[3:]
	course_already_in_DB, found_in_table = check_course_processed(check_course_db)

	if course_already_in_DB:
		print( "	already in DB" )
		write_to_file(f_courses_in_DB, str(check_course_db) + " / "+ str(found_in_table))
	else:
		check_url = "https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=" + check_course_number
		course_exists = driver_instance.check_course_exists(driver, check_url)

		if course_exists:
			print( "	exists (not in DB)" )
			write_to_file(f_courses_to_process, check_url + "|NoCurricula")
		else:
			print( "	does not exist" )
			write_to_file(f_invalid_courses, check_url)

# close the (web)driver
driver.close()	# close the current browser window
driver.quit()	# calls driver.dispose which closes all the browser windows and ends the webdriver session properly

# close filehandler
f_courses_to_process.close()
f_invalid_courses.close()
f_courses_in_DB.close()
