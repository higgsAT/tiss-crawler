# -*- coding: utf-8 -*-
#!/usr/bin/python3

import crawl
import sys

# initiate driver (instance)
crawl_delay = 10
driver_instance = crawl.crawler(False, 800, 600, crawl_delay)
driver = driver_instance.init_driver()

set_language = driver_instance.get_language(driver)



process_acad_prgm_name = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=37047|Architektur|Bachelorstudium Architektur"
driver_instance.process_acad_prgm(driver, process_acad_prgm_name)




#####################################################################################
driver.close()	# close the current browser window
driver.quit()	# calls driver.dispose which closes all the browser windows and ends the webdriver session properly

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







"""
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=37047|Architektur|Bachelorstudium Architektur
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=41934|Architektur|Masterstudium Architektur
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=42323|Architektur|Masterstudium Building Science and Environment
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59971|Architektur|Doktoratsstudium der Technischen Wissenschaften Architektur
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57488|Architektur|Katalog Freie Wahlfächer - Architektur
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=65645|Architektur|StEOP-Katalog Architektur (Ab WS2013)
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=37472|Bauingenieurwesen|Bachelorstudium Bauingenieurwesen
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=65319|Bauingenieurwesen|Masterstudium Bauingenieurwissenschaften
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59975|Bauingenieurwesen|Doktoratsstudium der Technischen Wissenschaften Bauingenieurwesen
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=64144|Bauingenieurwesen|Doktoratsstudium der Naturwissenschaften Bauingenieurwesen
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=64145|Bauingenieurwesen|Doktoratsstudium der Sozial- und Wirtschaftswissenschaften Bauingenieurwesen
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57482|Bauingenieurwesen|Katalog Freie Wahlfächer - Bauingenieurwesen
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=63744|Bauingenieurwesen|Transferable Skills - Bauingenieurwesen
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=65689|Bauingenieurwesen|Masterstudium Infrastrukturmanagement (Gemeinsames Studienprogramm der TU Wien und der UABG Sofia)
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=58908|Elektrotechnik|Bachelorstudium Elektrotechnik und Informationstechnik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=70844|Elektrotechnik|Masterstudium Elektrische Energietechnik und nachhaltige Energiesysteme
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=66304|Elektrotechnik|Masterstudium Embedded Systems
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=65354|Elektrotechnik|Masterstudium Energie- und Automatisierungstechnik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=65355|Elektrotechnik|Masterstudium Telecommunications
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=65356|Elektrotechnik|Masterstudium Mikroelektronik und Photonik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=70848|Elektrotechnik|Masterstudium Automatisierung und robotische Systeme
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59979|Elektrotechnik|Doktoratsstudium der Technischen Wissenschaften Elektrotechnik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57491|Elektrotechnik|Katalog Freie Wahlfächer - Elektrotechnik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=67184|Elektrotechnik|Doktoratsstudium der Naturwissenschaften Elektrotechnik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=67186|Elektrotechnik|Doktoratsstudium der Sozial und Wirtschaftswissenschaften Elektrotechnik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=36302|Geodäsie und Geoinformation|Bachelorstudium Geodäsie und Geoinformation
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=65375|Geodäsie und Geoinformation|Masterstudium Geodäsie und Geoinformation
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=63574|Geodäsie und Geoinformation|Internationales Masterstudium Cartography
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=60023|Geodäsie und Geoinformation|Doktoratsstudium der Technischen Wissenschaften Geodäsie und Geoinformation
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=65005|Geodäsie und Geoinformation|Doktoratsstudium der Naturwissenschaften Geodäsie und Geoinformation
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57483|Geodäsie und Geoinformation|Katalog Freie Wahlfächer - Geodäsie und Geoinformation
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=45518|Informatik|Bachelorstudium Data Engineering &amp; Statistics
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=45669|Informatik|Bachelorstudium Medieninformatik und Visual Computing / Studienplanänderung - 2. u. 3. Studienjahr erst ab 2023W im neuen Modus
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=45860|Informatik|Bachelorstudium Medizinische Informatik / Studienplanänderung - 2. u. 3. Studienjahr erst ab 2023W im neuen Modus
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=46100|Informatik|Bachelorstudium Software &amp; Information Engineering / Studienplanänderung - 2. u. 3. Studienjahr erst ab 2023W im neuen Modus
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=46319|Informatik|Bachelorstudium Technische Informatik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=55301|Informatik|Masterstudium Logic and Computation
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=55499|Informatik|Masterstudium Visual Computing
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=55935|Informatik|Masterstudium Media and Human-Centered Computing
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=56089|Informatik|Masterstudium Medizinische Informatik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=56290|Informatik|Masterstudium Software Engineering &amp; Internet Computing
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=56543|Informatik|Masterstudium Technische Informatik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59983|Informatik|Doktoratsstudium der Technischen Wissenschaften Informatik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59991|Informatik|Doktoratsstudium der Naturwissenschaften Informatik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57489|Informatik|Katalog Freie Wahlfächer - Informatik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=63764|Informatik|TU Wien Informatics Doctoral School
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=67625|Informatik|Doktoratsstudium der Sozial- und Wirtschaftswissenschaften Informatik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59995|Informatikmanagement|Doktoratsstudium der Sozial- und Wirtschaftswissenschaften Informatikmanagement
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=68865|Interfakultäre Studien|Bachelorstudium Umweltingenieurwesen
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=40842|Interfakultäre Studien|Masterstudium Materialwissenschaften
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=42680|Interfakultäre Studien|Masterstudium Biomedical Engineering
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=68744|Interfakultäre Studien|Masterstudium Computational Science and Engineering
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=70064|Interfakultäre Studien|Masterstudium Umweltingenieurwesen
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=70524|Interfakultäre Studien|Dr.-Studium der techn. Wissenschaften Materialwissenschaften
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=71045|Interfakultäre Studien|Doktoratsstudium der Naturwissenschaften Materialwissenschaften
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=40406|Lehramtsstudien|UF Darstellende Geometrie
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=62480|Lehramtsstudien|Doktoratsstudium der Naturwissenschaften UF Mathematik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=62481|Lehramtsstudien|Doktoratsstudium der Naturwissenschaften UF Darstellende Geometrie
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=62482|Lehramtsstudien|Doktoratsstudium der Naturwissenschaften UF Physik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=35194|Lehramtsstudien|Doktoratsstudium der Naturwissenschaften UF Chemie
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=62483|Lehramtsstudien|Doktoratsstudium der Naturwissenschaften UF Informatik und Informatikmanagement
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=37173|Maschinenbau|Bachelorstudium Maschinenbau
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59138|Maschinenbau|Masterstudium Maschinenbau
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=71144|Maschinenbau|Masterstudium Manufacturing and Robotics
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=65004|Maschinenbau|Doktoratsstudium der Sozial- und Wirtschaftswissenschaften Maschinenbau
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59999|Maschinenbau|Doktoratsstudium der Technischen Wissenschaften Maschinenbau
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57484|Maschinenbau|Katalog Freie Wahlfächer - Maschinenbau u. Wirtschaftsingenieurwesen-Maschinenbau
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=65264|Maschinenbau|Doktoratsstudium der Naturwissenschaften Maschinenbau
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=36777|Raumplanung und Raumordnung|Bachelorstudium Raumplanung und Raumordnung
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=41615|Raumplanung und Raumordnung|Masterstudium Raumplanung und Raumordnung
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=35193|Raumplanung und Raumordnung|Doktoratsstudium der Sozial- und Wirtschaftswissenschaften Raumplanung und Raumordnung
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=60003|Raumplanung und Raumordnung|Doktoratsstudium der Technischen Wissenschaften Raumplanung
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57485|Raumplanung und Raumordnung|Katalog Freie Wahlfächer - Raumplanung und Raumordnung
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=37748|Technische Chemie|Bachelorstudium Technische Chemie
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=65334|Technische Chemie|Masterstudium Technische Chemie
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=70804|Technische Chemie|Masterstudium Green Chemistry
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=63575|Technische Chemie|Masterstudium Chemie und Technologie der Materialien
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=60007|Technische Chemie|Doktoratsstudium der Technischen Wissenschaften Technische Chemie
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=60960|Technische Chemie|Doktoratsstudium der Naturwissenschaften Technische Chemie
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57481|Technische Chemie|Katalog Freie Wahlfächer - Technische Chemie
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=63529|Technische Mathematik|Bachelorstudium Technische Mathematik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=36058|Technische Mathematik|Bachelorstudium Statistik und Wirtschaftsmathematik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=36186|Technische Mathematik|Bachelorstudium Finanz- und Versicherungsmathematik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=67804|Technische Mathematik|Masterstudium Interdisciplinary Mathematics
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=64485|Technische Mathematik|Masterstudium Technische Mathematik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=64486|Technische Mathematik|Masterstudium Statistik-Wirtschaftsmathematik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=39925|Technische Mathematik|Masterstudium Finanz- und Versicherungsmathematik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=60011|Technische Mathematik|Doktoratsstudium der Technischen Wissenschaften Technische Mathematik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=35197|Technische Mathematik|Doktoratsstudium der Naturwissenschaften Technische Mathematik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=64576|Technische Mathematik|Katalog Gebundene Wahlfächer - Technische Mathematik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57487|Technische Mathematik|Katalog Freie Wahlfächer - Technische Mathematik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=37273|Technische Physik|Bachelorstudium Technische Physik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=42822|Technische Physik|Masterstudium Physikalische Energie- und Messtechnik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=43093|Technische Physik|Masterstudium Technische Physik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=60015|Technische Physik|Doktoratsstudium der Technischen Wissenschaften Technische Physik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=62484|Technische Physik|Doktoratsstudium der Naturwissenschaften Technische Physik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57490|Technische Physik|Katalog Freie Wahlfächer - Technische Physik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=37582|Verfahrenstechnik|Bachelorstudium Verfahrenstechnik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=44512|Verfahrenstechnik|Masterstudium Verfahrenstechnik und nachhaltige Produktion
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=60019|Verfahrenstechnik|Doktoratsstudium der Technischen Wissenschaften Verfahrenstechnik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57480|Verfahrenstechnik|Katalog Freie Wahlfächer - Verfahrenstechnik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=45300|Wirtschaftsinformatik|Bachelorstudium Wirtschaftsinformatik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=55088|Wirtschaftsinformatik|Masterstudium Business Informatics
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=67853|Wirtschaftsinformatik|Masterstudium Data Science
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=60031|Wirtschaftsinformatik|Doktoratsstudium der Sozial- und Wirtschaftswissenschaften Wirtschaftsinformatik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=64484|Wirtschaftsinformatik|Doktoratsstudium der Technischen Wissenschaften Wirtschaftsinformatik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57486|Wirtschaftsinformatik|Katalog Freie Wahlfächer - Wirtschaftsinformatik
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=37649|Wirtschaftsingenieurwesen - Maschinenbau|Bachelorstudium Wirtschaftsingenieurwesen - Maschinenbau
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=44651|Wirtschaftsingenieurwesen - Maschinenbau|Masterstudium Wirtschaftsingenieurwesen - Maschinenbau
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=60039|Wirtschaftsingenieurwesen - Maschinenbau|Doktoratsstudium der Sozial- und Wirtschaftswissenschaften Wirtschaftsingenieurwesen - Maschinenbau
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=60035|Wirtschaftsingenieurwesen - Maschinenbau|Doktoratsstudium der Technischen Wissenschaften Wirtschaftsingenieurwesen - Maschinenbau
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=64944|Universitätslehrgang|Energy College
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59380|Universitätslehrgang|MSc Engineering Management
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=35481|Universitätslehrgang|Immobilienwirtschaft &amp; Liegenschaftsmanagement
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59403|Universitätslehrgang|MSc Environmental Technology &amp; International Affairs
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=35545|Universitätslehrgang|MSc Immobilienmanagement und Bewertung
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59529|Universitätslehrgang|MSc Renewable Energy Systems
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=64946|Universitätslehrgang|MEng Nachhaltiges Bauen
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59318|Universitätslehrgang|Industrial Engineering
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=59460|Universitätslehrgang|Professional MBA Automotive Industry
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=35968|Universitätslehrgang|MEng Membrane Lightweight Structures
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=65385|Universitätslehrgang|Enterprise Risk Management
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=65384|Universitätslehrgang|MEng International Construction Project Management
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=61100|Universitätslehrgang|GmbH-Geschäftsführung für Führungskräfte
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=45085|Universitätslehrgang|Professional MBA Facility Management
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=46455|Universitätslehrgang|General Management MBA
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=46491|Universitätslehrgang|Professional MBA Entrepreneurship &amp; Innovation
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57006|Universitätslehrgang|Nachhaltiges Bauen
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=67604|Universitätslehrgang|Healthcare Facilities
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=68184|Universitätslehrgang|General Management MBA
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=69646|Universitätslehrgang|Management &amp; Technology MBA
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=67904|Erweiterungscurriculum|Erweiterungsstudium Innovation
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=68984|Erweiterungscurriculum|Erweiterungsstudium Digitale Kompetenzen
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57214|Weitere Kataloge|Transferable Skills
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=57023|Weitere Kataloge|Für alle Hörerinnen/Hörer
https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=67824|Weitere Kataloge|Austauschmodule Life Sciences
"""



driver.close()	# close the current browser window
driver.quit()	# calls driver.dispose which closes all the browser windows and ends the webdriver session properly
