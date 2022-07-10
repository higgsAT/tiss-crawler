# -*- coding: utf-8 -*-
#!/usr/bin/python3

import crawl
import time
import sqlhandler
from sys import exit

# crawling events testing
driver_instance = crawl.crawler(False, 800, 600, 2)

driver = driver_instance.init_driver()

driver_instance.tiss_login(driver)

#page_to_fetch = "https://tiss.tuwien.ac.at/course/courseDetails.xhtml?dswid=5214&dsrid=967&courseNr=254037&semester=2021S"
#driver_instance.fetch_page(driver, page_to_fetch)

wait = input("Press Enter to continue1.")

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



starting_page = "https://tiss.tuwien.ac.at/curriculum/studyCodes.xhtml"
acad_program_list = driver_instance.fetch_academic_programs(driver, starting_page)
print (acad_program_list)
print(len(acad_program_list))



wait = input("Press Enter to continue4.")

driver_instance.close_driver(driver)
print ('\nexiting')
