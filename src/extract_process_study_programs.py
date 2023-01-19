# -*- coding: utf-8 -*-
#!/usr/bin/python3

import crawl
import sys

from config import *

"""
# initiate driver (instance)
crawl_delay = 10
driver_instance = crawl.crawler(False, 800, 600, crawl_delay)
driver = driver_instance.init_driver()

set_language = driver_instance.get_language(driver)
"""

return_collected_courses_list = {'2022S': {'1. Semester': ['253G61', '104590', '264219', '264232', '253G62', '253G63', '259600', '251866'], '2. Semester': ['264220', '253H82', '259601', '259604', '259606', '251867'], '3. Semester': ['264218', '260658', '253G65', '253G66', '259605', '251868'], '4. Semester': ['260657', '253G60', '260659', '259602', '253G69', '251869'], '5. Semester': ['253G68', '259599', '259603', '251870', '259597', '253G67'], '6. Semester': ['253G70', '253H43', '280767', '259598', '251871', '251872', '251873', '259611', '253H00', '251874', '260674', '260675', '253H29', '251883', '251885', '259629', '264222', '264224', '264225', '259647', '259648', '253H64', '259649', '259650', '251887', '260726', '264226', '251898', '264231', '253I20', '251903', '259671', '253I36', '251916', '259676', '253161', '260757', '253G93', '253H01', '253H07', '253H10', '253H12', '253H37', '253H40', '253H54', '253H58', '253H60', '253H65', '253H67', '253H69', '253H71', '253H73', '253H83', '253H84', '253H91', '253H92', '253H93', '260727', '260728', '260730', '253I02', '253I15', '253I21', '253I26', '253I28', '253I32', '253I33', '253I37', '253I41', '253I43', '253I45', '253I48', '259686', '260793', '253J28', '253I58', '253I60', '253I69', '253I71', '253I72', '253I82', '253I83', '253I88', '253I89', '260770', '260773', '260775', '253I98', '253J00', '253J03', '253J10', '253J12', '253J14', '253J16', '253J19'], 'Ohne Semesterempfehlung': ['251169', '251730', '251739', '251911', '251913', '251917', '264212', '015576', '251833', '251834', '251851', '251888', '251902', '251914', '251915', '181200', '120095', '253H63', '264177', '264179', '253676', '253C29', '352031', '253498', '253499', '259446', '264191', '260576', '015088', '015011', '015035', '015067', '253A35', '253G83', '258032', '264031', '264124', '264125', '257036', '264223', '253G74', '253G75', '253G71', '253118', '259646', '253G73', '253H77', '251804', '251818', '251113', '251894', '253040', '259627', '259659', '259664', '259619', '259651', '259632', '259666', '253062', '259677', '259631', '259665', '260300', '259630', '260668', '251922', '251700', '253J06']}, '2022W': {'1. Semester': ['253G61', '104590', '264219', '253G62', '253G63', '259600', '251866'], '2. Semester': ['259601', '259604', '259606', '264220', '253H82', '251867'], '3. Semester': ['264218', '260658', '253G65', '253G66', '259605', '251868'], '4. Semester': ['259602', '260657', '253G60', '260659', '253G69', '251869'], '5. Semester': ['253G67', '253G68', '259599', '259603', '251870', '259597'], '6. Semester': ['280767', '251871', '259611', '251874', '260674', '253H29', '251883', '264222', '264224', '264225', '259647', '259648', '259650', '259671', '253161', '259686', '260793', '253J28', '253H07', '253I58', '253I60', '253I69', '253I71', '253I72', '253I82', '253I83', '253I88', '253I89', '260770', '260773', '260775', '253I98', '253J00', '253J03', '253J10', '253J12', '253J14', '253J16', '253J19', '253G70', '253H43', '259598', '251872', '251873', '253H00', '260675', '251885', '259629', '253H64', '259649', '251887', '260726', '264226', '251898', '264231', '253I20', '251903', '253I36', '251916', '259676', '260757', '253G93', '253H01', '253H10', '253H12', '253H37', '253H40', '253H54', '253H58', '253H60', '253H65', '253H67', '253H69', '253H71', '253H73', '253H83', '253H84', '253H91', '253H92', '253H93', '260727', '260728', '260730', '253I02', '253I15', '253I21', '253I26', '253I28', '253I32', '253I33', '253I37', '253I41', '253I43', '253I45', '253I48'], 'Ohne Semesterempfehlung': ['251169', '251730', '251917', '015576', '251833', '251834', '251851', '251915', '181200', '251922', '120095', '264179', '253676', '352031', '253498', '253499', '259446', '264191', '260576', '015088', '015011', '015035', '015067', '253A35', '258032', '264031', '264124', '257036', '253G74', '253G75', '253G71', '253118', '259646', '253G73', '251818', '251700', '259627', '259659', '259619', '259632', '259666', '253062', '259631', '259665', '260300', '253J06', '251739', '251911', '251913', '264212', '251888', '251902', '251914', '253H63', '264177', '253C29', '253G83', '264125', '264223', '253H77', '251804', '251113', '251894', '253040', '259664', '259651', '259677', '259630', '260668']}, '2023S': {'1. Semester': ['253G61', '104590', '264219', '253G62', '253G63', '259600', '251866'], '2. Semester': ['259601', '259604', '259606', '264220', '253H82', '251867'], '3. Semester': ['264218', '260658', '253G65', '253G66', '259605', '251868'], '4. Semester': ['259602', '260657', '253G60', '260659', '253G69', '251869'], '5. Semester': ['253G67', '253G68', '259599', '259603', '251870', '259597'], '6. Semester': ['280767', '251871', '259611', '251874', '260674', '253H29', '251883', '264222', '264224', '264225', '259647', '259648', '259650', '259671', '253161', '259686', '260793', '253J28', '253H07', '253I58', '253I60', '253I69', '253I71', '253I72', '253I82', '253I83', '253I88', '253I89', '260770', '260773', '260775', '253I98', '253J00', '253J03', '253J10', '253J12', '253J14', '253J16', '253J19', '253G70', '253H43', '259598', '251872', '251873', '253H00', '260675', '251885', '259629', '253H64', '259649', '251887', '260726', '264226', '251898', '264231', '253I20', '251903', '253I36', '251916', '259676', '260757', '253G93', '253H01', '253H10', '253H12', '253H37', '253H40', '253H54', '253H58', '253H60', '253H65', '253H67', '253H69', '253H71', '253H73', '253H83', '253H84', '253H91', '253H92', '253H93', '260727', '260728', '260730', '253I02', '253I15', '253I21', '253I26', '253I28', '253I32', '253I33', '253I37', '253I41', '253I43', '253I45', '253I48'], 'Ohne Semesterempfehlung': ['251169', '251730', '251917', '015576', '251833', '251834', '251851', '251915', '181200', '251922', '120095', '264179', '253676', '352031', '253498', '253499', '259446', '264191', '260576', '015088', '015011', '015035', '015067', '253A35', '258032', '264031', '264124', '257036', '253G74', '253G75', '253G71', '253118', '259646', '253G73', '251818', '251700', '259627', '259659', '259619', '259632', '259666', '253062', '259631', '259665', '260300', '253J06', '251739', '251911', '251913', '264212', '251888', '251902', '251914', '253H63', '264177', '253C29', '253G83', '264125', '264223', '253H77', '251804', '251113', '251894', '253040', '259664', '259651', '259677', '259630', '260668']}, 'program_code': '033 243'}



process_acad_prgm_name = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=37047|Architektur|Bachelorstudium Architektur"
"""
return_collected_courses_list = driver_instance.process_acad_prgm(driver, process_acad_prgm_name)
"""

# unpack the returned information
insert_program_code = '"' + return_collected_courses_list['program_code'] + '"'
print("insert_program_code: " + insert_program_code)

#print("RETURNRETURN:")
#print(return_collected_courses_list)

return_coll_courses_keys = list ( return_collected_courses_list.keys() )

print("\n\n")
print(return_coll_courses_keys)
print("\n\n")

insert_acad_prgm_de = '"' + process_acad_prgm_name.split("|")[1] + '"'
insert_subprgm_title_de = '"' + process_acad_prgm_name.split("|")[2] + '"'

insert_acad_prgm_en = '"' + process_acad_prgm_name.split("|")[1] + '"'
insert_subprgm_title_en = '"' + process_acad_prgm_name.split("|")[2] + '"'

# blank (set in the DB)
insert_id_courses = "0";

# file to write the insert (sql) statements
write_folder = root_dir + logging_folder + study_prgms_folder
f_study_programs_insert = open(write_folder + "study_programs_insert" + ".txt", "a")


for _ in return_coll_courses_keys:
	if _ != "program_code":
		process_entry = return_collected_courses_list[_]
		#print(_ + " | " + academ_program_name_de + ":")

		process_entry_keys = list ( process_entry.keys() )
		for __ in process_entry_keys:
			#print(__)
			#print(process_entry[__])
			for ___ in process_entry[__]:
				# generate DB insert variables
				insert_unique_id = '"' + ___ + __ + _ + insert_subprgm_title_de[1:-1] + insert_acad_prgm_de[1:-1] + '"'
				insert_course_number = '"' + ___[:3] + "." + ___[3:] + '"'
				insert_semester = '"' + _ + '"'
				insert_subsemester = '"' + __ + '"'

				insert_statement = (
				  "(" +
						insert_unique_id + ", " +
						insert_id_courses + ", " +
						insert_course_number + ", " +
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
			print("\n")
		#print(process_entry_keys)

		#print(process_entry)
		print("\n\n")


f_study_programs_insert.close()

"""
#####################################################################################
driver.close()	# close the current browser window
driver.quit()	# calls driver.dispose which closes all the browser windows and ends the webdriver session properly
"""
sys.exit()
#####################################################################################



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

# extract courses for the study programs (depending on semester)
for process_acad_prgm in acad_program_list1:
	print (process_acad_prgm + " | " + acad_program_list_lang1, end = "\n")

for process_acad_prgm in acad_program_list2:
	print (process_acad_prgm + " | " + acad_program_list_lang2, end = "\n")


driver.close()	# close the current browser window
driver.quit()	# calls driver.dispose which closes all the browser windows and ends the webdriver session properly
