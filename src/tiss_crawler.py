# -*- coding: utf-8 -*-
#!/usr/bin/python3

import os
import sqlhandler
import time

import crawl
import pylogs

# set folders / files
logging_folder = "logs/"
logging_academic_programs = "academic_programs.txt"
logging_queued_courses = "queued_courses.txt"

# initiate driver (instance)
driver_instance = crawl.crawler(False, 800, 600, 5)
driver = driver_instance.init_driver()

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








print(acad_program_list)
print(len(acad_program_list))


driver_instance.close_driver(driver)
exit()














pylogs.test()
pylogs.test()
pylogs.test()

logging = pylogs.logs("logs/", "testlog")

for i in range(0, 20):
	logging.append_to_log("MU" + str(i))
	time.sleep(0.25)

exit()


driver_instance = crawl.crawler(False, 800, 600, 5)
driver = driver_instance.init_driver()

#driver_instance.tiss_login(driver)

#page_to_fetch = "https://tiss.tuwien.ac.at/course/courseDetails.xhtml?dswid=5214&dsrid=967&courseNr=254037&semester=2021S"
#driver_instance.fetch_page(driver, page_to_fetch)

#wait = input("Press Enter to continue1.")

"""
#entrance_point = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=37273"
#driver_instance.fetch_page(driver, entrance_point)

page_to_fetch = "https://tiss.tuwien.ac.at/course/courseDetails.xhtml?dswid=5214&dsrid=967&courseNr=254037&semester=2021S"
driver_instance.fetch_page(driver, page_to_fetch)
determine_language = driver_instance.get_language(driver)
print("get lang2: " + str(determine_language))


wait = input("Press Enter to continue3.")

driver_instance.switch_language(driver)

driver_instance.fetch_page(driver, page_to_fetch)
determine_language = driver_instance.get_language(driver)
print("get lang2: " + str(determine_language))
"""


"""
starting_page = "https://tiss.tuwien.ac.at/curriculum/studyCodes.xhtml"

# get the links to all academic programs
acad_program_list = driver_instance.extract_academic_programs(driver, starting_page, "key")
print(acad_program_list)
print(len(acad_program_list))

extracted_course_URLs = driver_instance.extract_courses(driver, acad_program_list[0])
#print(extracted_course_URLs)
#print(len(extracted_course_URLs))
"""


#driver_instance.extract_course_info(driver, extracted_course_URLs[0], True)

#URL = "https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=138017"
#URL = "https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=389158"
#URL = "https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=253J14"
#URL = "https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=103064" #linalg
URL = "https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=136019" #Q1


driver_instance.extract_course_info(driver, URL, True)

driver_instance.close_driver(driver)
print ('\nexiting')
