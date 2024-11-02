# -*- coding: utf-8 -*-
#!/usr/bin/python3

import crawl
import sys

from config import *

# TODO: set language (subsemester) to english (DB!)

write_folder = root_dir + logging_folder + study_prgms_folder
study_prgms_result_path = write_folder + "study_programs_insert" + ".txt"

# check if file exist. If not -> cout warning and stop the program
try:
	f_study_programs_insert = open(study_prgms_result_path, "a")
except Exception as e:
	print("error openening file (" + str(e) + ") -> create file '" + study_prgms_result_path + "'")
	sys.exit()

# initiate driver (instance)
crawl_delay = 20
driver_instance = crawl.crawler(False, 800, 600, crawl_delay)
driver = driver_instance.init_driver()

# log in to get all available semester options (not logged in -> max. ~ 3 semesters available)
# while being logged in, the SELECT options reach further into the past (~ 6 semester), using
# URL $_GET-parameters, it'S possible to even go (much) further back into time without loggin in!
driver_instance.tiss_login(driver)

# determine the set language of TISS
set_language = driver_instance.get_language(driver)

# file to write the insert (sql) statements. This (text)file contains
# all extracted information ready to be inserted into the database. This yields
# a lot of information (= lines/DB-rows) to be inserted. At the moment, no mass
# insertion is available and this method (extraction -> textfile -> insertion via,
# e.g., phpMyAdmin is significantly faster than insertion via sql in python.
write_folder = root_dir + logging_folder + study_prgms_folder
f_study_programs_insert = open(write_folder + "study_programs_insert" + ".txt", "a")

# get a list of academic programs (fetch both languages -> en/ger)
academic_program_URL = "https://tiss.tuwien.ac.at/curriculum/studyCodes.xhtml"

# language 1
acad_program_list_lang1 = set_language
acad_program_list1 = driver_instance.extract_academic_programs(
	driver,
	academic_program_URL
)

# switch language
driver_instance.switch_language(driver)
set_language = driver_instance.get_language(driver)

# language 2
acad_program_list_lang2 = set_language
acad_program_list2 = driver_instance.extract_academic_programs(
	driver,
	academic_program_URL
)

# sanity check
if len(acad_program_list1) != len(acad_program_list2):
	raise Exception("Mismatching length of lists containing the study programs (ger != en)")

# skip to a certain point
_start = 80

# extract courses for the study programs (depending on semester)
# set_language = "de" or "en"
for _ in range( _start, len( acad_program_list1 ) ):
	print( str(_) + " " + acad_program_list_lang1 + " processing: " + acad_program_list1[_] )
	print( str(_) + " " + acad_program_list_lang2 + " processing: " + acad_program_list2[_] )

	# extract information about the study program (take either language -> does not matter)
	return_collected_courses_list = driver_instance.process_acad_prgm(driver, acad_program_list1[_], True)

	## unpack the returned information
	# study code (123 456, 555 666, etc.)
	process_study_code = return_collected_courses_list['program_code']

	# some academic programs don't have program codes -> if not valid format set to empty string
	if not process_study_code[:3].isnumeric() or not process_study_code[4:].isnumeric() or process_study_code[3] != " ":
		print("no study code: " + process_study_code)
		process_study_code = ""

	insert_program_code = '"' + process_study_code + '"'
	print("insert_program_code: " + insert_program_code)

	#print("RETURNRETURN:")
	#print(return_collected_courses_list)

	return_coll_courses_keys = list ( return_collected_courses_list.keys() )

	print("\n\n")
	print(return_coll_courses_keys)
	print("\n\n")

	# set the academic program name (architecture, electrical engineering, etc.), as
	# well as the name of the subprogram (bachelor arch, master arch, etc.) depending
	# on the language.
	if acad_program_list_lang1 == "de":
		insert_acad_prgm_de = '"' + acad_program_list1[_].split("|")[1] + '"'
		insert_subprgm_title_de = '"' + acad_program_list1[_].split("|")[2] + '"'

		insert_acad_prgm_en = '"' + acad_program_list2[_].split("|")[1] + '"'
		insert_subprgm_title_en = '"' + acad_program_list2[_].split("|")[2] + '"'
	else:
		insert_acad_prgm_de = '"' + acad_program_list2[_].split("|")[1] + '"'
		insert_subprgm_title_de = '"' + acad_program_list2[_].split("|")[2] + '"'

		insert_acad_prgm_en = '"' + acad_program_list1[_].split("|")[1] + '"'
		insert_subprgm_title_en = '"' + acad_program_list1[_].split("|")[2] + '"'

	# format course numbers / additional info into sql-inserts and
	# write this into a file.
	for _ in return_coll_courses_keys:
		# program code is also in the dict -> no semester info in this key => ignore
		if _ != "program_code":
			process_entry = return_collected_courses_list[_]
			#print(_ + " | " + academ_program_name_de + ":")

			process_entry_keys = list ( process_entry.keys() )

			# count total number of courses for this semester. If this number is
			# zero, don't proceed any further (no entry into DB)
			amt_courses = 0
			for __ in process_entry_keys:
				for ___ in process_entry[__]:
					amt_courses = amt_courses + 1

			print("amt_courses: " + str(amt_courses))

			if amt_courses > 0:
				for __ in process_entry_keys:
					#print(__)
					print(process_entry[__])

					# format courses, join them
					join_formatted_courses = ""
					for ___ in process_entry[__]:
						if join_formatted_courses == "":
							join_formatted_courses = ___[:3] + "." + ___[3:]
						else:
							join_formatted_courses = join_formatted_courses + "|" + ___[:3] + "." + ___[3:]

					# generate DB insert variables
					insert_unique_id = '"' +  __ + _ + insert_subprgm_title_de[1:-1] + insert_acad_prgm_de[1:-1] + '"'
					insert_course_numbers = '"' + join_formatted_courses + '"'
					insert_semester = '"' + _ + '"'
					insert_subsemester = '"' + __ + '"'

					insert_statement = (
					  "(" +
							insert_unique_id + ", " +
							insert_course_numbers + ", " +
							insert_semester + ", " +
							insert_subsemester + ", " +
							insert_subprgm_title_de + ", " +
							insert_subprgm_title_en + ", " +
							insert_acad_prgm_de + ", " +
							insert_acad_prgm_en + ", " +
							insert_program_code +
						"),"
						)
					print(insert_statement)
					f_study_programs_insert.write(insert_statement + "\n")
						#("uniqueID2", 2, "123.456", "2022W", "subDE", "subEN", "aPOde", "aPOen", "456 789"),
					#print("\n")
			#print(process_entry_keys)

			#print(process_entry)
			#print("\n\n")

	# manual break
	#break

f_study_programs_insert.close()

driver.close()	# close the current browser window
driver.quit()	# calls driver.dispose which closes all the browser windows and ends the webdriver session properly
