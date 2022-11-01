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

def sql_insert_courses(return_info_dict, pylogs_filepointer):
	"""Insert data into a SQL database
	"""
	pylogs.write_to_logfile(f_runtime_log, 'inserting into the database')

	"""
	# unpack the information and insert it into the SQL db
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	semester_dict_keys = list( return_info_dict.keys() )
	for key_semesters in semester_dict_keys:
		print("KEY: " + key_semesters)
		print("-----------------------------------------------------------\n")
		chosen_semester_dict = return_info_dict[key_semesters]
		for
	"""


	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~1:\n")
	print(return_info_dict)
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~2:\n")
	print(*return_info_dict.items(), sep='\n\n')
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~3:\n")
	semester_dict_keys = list( return_info_dict.keys() )
	print( str(semester_dict_keys) )
	# ['2022Wen', '2022Wde', '2021Wen', '2021Wde']
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4:\n")
	chosen_semester_dict = return_info_dict[semester_dict_keys[0]]
	print(chosen_semester_dict)
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~5:\n")
	print(*chosen_semester_dict.items(), sep='\n\n')
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~6:\n")
	dict_keys2 = list( chosen_semester_dict.keys() )
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~7:\n")
	print(dict_keys2)
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8:\n")
	print(chosen_semester_dict[dict_keys2])
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~9:\n")


	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~:\n")








test_dat = {'2022Sen': {'page_fetch_lang': 'en', 'course number': '253.G70', 'course title': 'Baudurchführung und AVA', 'semester': '2022S', 'type': 'VO', 'sws': '3.0h', 'ECTS': '3.0EC', 'Merkmale': '<ul>        <li>Semester hours: 3.0        </li>        <li>Credits: 3.0        </li>        <li>Type: VO Lecture        </li>        <li>LectureTube course        </li>            <li><span title="Course is held on-site as well as online">Format: Hybrid</span>            </li>    </ul>', 'Lernergebnisse': '<div><p>After successful completion of the course, students are able to apply the acquired basic knowledge on the structure of architectural projects, the methods of scheduling and cost planning, the execution of procurement procedures and the conclusion of building contracts, as well as on the tasks of ÖBA.</p>        </div>', 'Inhalt der Lehrveranstaltung': '<div><p>V1&nbsp;&nbsp; &nbsp;Introduction to the contents and aims of the course, script, literature. Phases of planning and construction processes, scope of services, interfaces and communication between the parties involved (client, architect, planners, construction companies). Performance and remuneration models in architecture and engineering.</p><p>V2&nbsp;&nbsp; &nbsp;Basics of scheduling: types of schedules, critical path analysis, workflow planning and time management.</p><p>V3&nbsp;&nbsp; &nbsp;Basics of cost planning: cost calculation with parameters, element costing according to ÖN B 1801-1 and DIN 276.</p><p>V4&nbsp;&nbsp; &nbsp;Construction contract: ÖNorm B 2110, norms on contracts for work B 22xx and H22xx, VOB.</p><p>V5&nbsp;&nbsp; Tender procedure: types of tenders for construction and delivery performances according to ÖN A 2050 and BVergG 2018, structure, procedural and contractual provisions, technical clauses, technical specifications.</p><p>V6 &nbsp;&nbsp; Service description: data structur according to ÖN A 2063, specifications, constructional vs. functional specifications, examples, quantity calculation, data exchange, AVA programs.</p><p>V7 &nbsp;&nbsp; Tenders / Tender vettings / award decision: best bid vs. lowest bid procedures, eligibility, selection and award criteria, tender, examination of tenders, determination of the best bidder, award, legal authorities according to BVergG.</p><p>V8 &nbsp;&nbsp; Site supervision: tasks and methods of site supervision, coordinates and quality control of construction works, delay, examination of measurement and accounting, formal takeover, warranty, correction of defects, sample letters, risks. safety on construction sites according to BauKG: coordination of planning and on-site, SiGe-Plan, documents for subsequent works.</p><p>V9&nbsp;&nbsp; &nbsp;Basics of cost calculation according to ÖN B 2061, K-sheets (K3, K4, K6, K7), price conversion according to ÖN B 2111, subsequent audit.</p>    </div>', 'Methoden': '<div><p>-&nbsp;&nbsp;&nbsp; Lectures<br>-&nbsp;&nbsp;&nbsp; Acquisition of basic terminology<br>-&nbsp;&nbsp;&nbsp; Calculate Exercise Examples<br>-&nbsp;&nbsp;&nbsp; Discussion of case studies<br>-&nbsp;&nbsp;&nbsp; Guest Lectures</p>        </div>', 'Prüfungsmodus': 'Written', 'Weitere Informationen0': '<div><p><strong>Consultation hours</strong>: Fr., 12:00 - 13:00 Uhr via Zoom-Meeting.<br>The link to the Zoom-Meeting is provided in the TUWEL online-course (see „Zum TUWEL Online-Kurs“).</p><p><strong>Exam review</strong>: digital.<br>Please use your university email address to hannes.wind@tuwien.ac.at.</p><p><strong>LectureTube Live</strong>:<br>The live stream is provided in the TUWEL online-course (see „Zum TUWEL Online-Kurs“).</p><p><strong>LectureTube Aufzeichnung ... lecture recording</strong>:<br>The lecture recording is provided in the TUWEL online-course (see „Zum TUWEL Online-Kurs“).</p><p><strong><span>Note</span></strong>:<br><span>In</span> <span>the</span> <span>event</span> <span>of</span> <span>a</span> <span>changed</span> <span>Corona</span> <span>situation</span>, <span>the</span> <span>format</span> <span>may</span> <span>change</span> (<span>e.</span> <span>g.</span> <span>switching</span> <span>to</span> <span>pure</span> <span>distance</span> <span>learning</span>).</p>        </div>', 'Vortragende Personen': ['Wind, Hannes', 'Skolud, Matthias'], 'Institut': 'E253 Institute of Architecture and Design', 'Leistungsnachweis': '<div><p>-&nbsp;&nbsp; &nbsp;Written examination<br>-&nbsp;&nbsp; &nbsp;Examination questions: see Register „Documents“ (from Juni 2022)<br>-&nbsp;&nbsp; &nbsp;Duration of examination: 90 minutens<br>-&nbsp;&nbsp; &nbsp;No aids (documents, electronic devices, calculators, mobile phones, headphones, etc. ) may be used during the examination. <br><br><strong>Deregistration from examinations according to Mitteilungsblatt 2014, 3. Stück; Nr.22</strong><br>§ 18a. (1) Die Studierenden sind berechtigt, sich bis spätestens zwei Arbeitstage vor dem Prüfungstag mündlich, schriftlich oder elektronisch bei der Prüferin/beim Prüfer oder bei der Studiendekanin/beim Studiendekan von der Prüfung abzumelden.<br>(2) Erscheinen Studierende nicht zu einer Prüfung, ohne sich gemäß Abs. 1 abgemeldet zu haben, so ist die Studiendekanin/der Studiendekan auf Vorschlag der Prüferin/des Prüfers berechtigt, diese Studierenden für einen Zeitraum von acht Wochen von der Anmeldung zu dieser Prüfung auszuschließen. Diese ordnungsrechtliche Frist beginnt mit dem Prüfungstag, an dem die/der Studierende trotz aufrechter Anmeldung ohne vorherige Abmeldung nicht erschienen ist. Die betroffenen Studierenden sind von der Sperre auf geeignete Weise zu informieren. <br>(3) Kann die/der Studierende nachweisen, dass sie/er durch einen triftigen Grund (zB. Unfall) oder einen anderen besonders berücksichtigungswürdigen Grund an einer rechtzeitigen Abmeldung gemäß Abs. 1 gehindert gewesen ist, ist die Sperre aufzuheben.</p>        </div>', 'LVA-Anmeldung': '<table class="standard big">                    <thead>                    <tr>                        <th>Begin</th>                        <th>End</th>                        <th>Deregistration end</th>                    </tr>                    </thead>                    <tbody><tr>                        <td>01.03.2022 08:00                        </td>                        <td>28.02.2023 23:55                        </td>                        <td>28.02.2023 23:55                        </td>                    </tr>                </tbody></table>        <h3>Precondition        </h3>        <p>The student has to be enrolled for at least one of the studies listed below         </p>        <ul>                <li><a href="/curriculum/public/curriculum.xhtml?key=37047">033 243 Architecture</a>                </li>                <li><a href="/curriculum/public/curriculum.xhtml?key=41934">066 443 Architecture</a>                </li>                <li><a href="/curriculum/public/curriculum.xhtml?key=42323">066 444 Building Science and Environment</a>                </li>        </ul>', 'Curricula': ['033 243 Architecture', ['6. Semester', '<img id="j_id_2o:j_id_e2:j_id_e3:0:precondSteopSteg" src="/course/javax.faces.resource/STEOP_OK.png.xhtml?ln=img" alt="STEOP" style="height: 12pt">', '']], 'Literatur': '<div><p><strong>PRIEBERNIG: KONSTRUIEREN+BAUEN. AVA · TERMINE · KOSTEN · ÖBA, TU Verlag, Wien 2015</strong>, ISBN 978-3-903024-09-0, <a href="http://www.tuverlag.at">www.tuverlag.at</a>, <a href="http://www.grafischeszentrum.com">www.grafischeszentrum.com</a>.<br>Notice: The book relates to the BVergG 2006. The lecture relates to the curent BVergG 2018.<br><br><strong>Skriptum</strong><br><strong>PRIEBERNIG: BAUDURCHFÜHRUNG + AVA 2019</strong>, TU Verlag, Wien 2019, <a href="http://www.tuverlag.at">www.tuverlag.at</a>, <a href="http://www.grafischeszentrum.com">www.grafischeszentrum.com</a>.<br><br>More detailed information can be found at the description in german.</p>    </div>        <ul>            <li><a href="/education/course/documents.xhtml?courseNr=253G70&amp;semester=2022S">Go to Course Materials</a>            </li>        </ul>', 'Vorkenntnisse': '<div><p><strong>Courses of the 1st to 5th semester Bachelor programme Architecture (033 243).</strong></p>        </div>', 'Vorausgehende Lehrveranstaltungen': '<ul>                <li><a href="courseDetails.xhtml?courseNr=253G63">253.G63 VO Hochbau 1</a>                </li>                <li><a href="courseDetails.xhtml?courseNr=253G66">253.G66 VO Hochbau 2</a>                </li>                <li><a href="courseDetails.xhtml?courseNr=253G69">253.G69 VO Hochbau 3</a>                </li>        </ul>', 'Sprache': 'German'}, '2022Sde': {'page_fetch_lang': 'de', 'course number': '253.G70', 'course title': 'Baudurchführung und AVA', 'semester': '2022S', 'type': 'VO', 'sws': '3.0h', 'ECTS': '3.0EC', 'Merkmale': '<ul>        <li>Semesterwochenstunden: 3.0        </li>        <li>ECTS: 3.0        </li>        <li>Typ: VO Vorlesung        </li>        <li>LectureTube Lehrveranstaltung        </li>            <li><span title="Lehrveranstaltung wird in Präsenz- und Onlineformaten abgehalten">Format der Abhaltung: Hybrid</span>            </li>    </ul>', 'Lernergebnisse': '<div><p>Nach positiver Absolvierung der Lehrveranstaltung sind Studierende in der Lage das erworbene Grundwissen zu der Struktur von Architekturprojekten, den Methoden der Termin- und Kostenplanung, der Durchführung von Vergabeverfahren und dem Schließen von Bauverträgen, sowie zu den Aufgaben der ÖBA anzuwenden.</p>        </div>', 'Inhalt der Lehrveranstaltung': '<div><p>V1&nbsp;&nbsp; &nbsp;Einführung in die VO-Inhalte und Lehrziele, Skriptum, Literatur. Phasengliederung der Planungs- und Bauprozesse. Aufgaben und Schnittstellen der Projektbeteiligten (Bauherr, Architekt, Fachplaner, Baufirmen). Leistungs- und Vergütungsmodelle für Architekten- und Ingenieurleistungen.</p><p>V2&nbsp;&nbsp; &nbsp;Grundlagen der Terminplanung: Terminplan-Arten, Netzplantechnik, Bauablauf- und Bauzeitplanung.</p><p>V3&nbsp;&nbsp; &nbsp;Grundlagen der Kostenplanung, Kostenberechnung nach Kennwerten, Elementkostenberechnung gem. ÖN B 1801-1 und DIN 276.</p><p>V4&nbsp;&nbsp; &nbsp;Bauvertrag: ÖNORM B 2110, Werkvertragsnormen B 22xx und H22xx, VOB.</p><p>V5&nbsp; &nbsp; Ausschreibung: Vergabearten und -verfahren für Bau- und Lieferleistungen gem. ÖN A 2050 und BVergG 2018., Gliederung, Verfahrens- und Vertragsbestimmungen, Technikklauseln, Technische Spezifikationen.</p><p>V6 &nbsp;&nbsp; Leistungsbeschreibung/-verzeichnis LB-/LV-Datenstruktur gem. ÖNORM A 2063, Leistungsverzeichnis [LV], konstruktive vs. funktionale Leistungsbeschreibung, Mengenermittlung. Datenaustausch, AVA-Programme.</p><p>V7 &nbsp;&nbsp; Angebot / Angebotsprüfung / Zuschlag: Best- vs. Billigstbieter-Vergabeverfahren, Eignungs-, Auswahl- und Zuschlagskriterien, Ausschreibung, Angebot, Angebotsprüfung, Bestbieterermittlung, Zuschlagsentscheidung, Rechtsinstanzen gem. BVergG.</p><p>V8 &nbsp;&nbsp; Örtliche Bauaufsicht [ÖBA]: Aufgaben und Methodik der ÖBA, Koordination und Qualitätskontrolle der Bauausführung, Aufmaß- und Rechnungsprüfung, Verzug, Förmliche Übernahme, Gewährleistung, Mängelbehebung, Musterbriefe, Risiken der ÖBA. Sicherheit auf Baustellen gem. BauKG: Planungs- und Baustellenkoordination, SiGe-Plan, Unterlage für spätere Arbeiten.</p><p>V9&nbsp;&nbsp; &nbsp;Grundlagen der Kalkulation von Baupreisen gem. ÖN B 2061, K-Blätter (K3, K4, K6, K7), Preisumrechnung gem. ÖN B 2111, Nachtragsprüfung.</p>    </div>', 'Methoden': '<div><p>-&nbsp;&nbsp;&nbsp; Vorlesungen<br>-&nbsp;&nbsp;&nbsp; Aneignung grundlegender Begrifflichkeit<br>-&nbsp;&nbsp;&nbsp; Rechnen von Übungsbeispielen<br>-&nbsp;&nbsp;&nbsp; Diskussion von Fallbeispielen<br>-&nbsp;&nbsp;&nbsp; Gastvorträge</p>        </div>', 'Prüfungsmodus': 'Schriftlich', 'Weitere Informationen0': '<div><p><strong>Sprechstunden</strong>: Fr., 12:00 - 13:00 Uhr via Zoom-Meeting.<br>Den Link zum jeweiligen Zoom-Meeting können Sie dem TUWEL Online-Kurs entnehmen (siehe „Zum TUWEL Online-Kurs“).</p><p><strong>Prüfungseinsicht</strong>: digital.<br>Bitte wenden Sie sich unter Verwendung Ihrer Hochschulemailadresse an hannes.wind@tuwien.ac.at.</p><p><strong>LectureTube Live</strong>:<br>Den Live Stream können Sie im TUWEL Online-Kurs einsehen (siehe „Zum TUWEL Online-Kurs“).</p><p><strong>LectureTube Aufzeichnung</strong>:<br>Die Vorlesungsaufzeichnungen können Sie im TUWEL Online-Kurs einsehen (siehe „Zum TUWEL Online-Kurs“).</p><p><strong>Hinweis</strong>:<br>Im Falle einer geänderten Corona-Situation, kann es zu Änderungen des Formats kommen (z.B. Umstieg auf reines Distance-Learning).</p>        </div>', 'Vortragende Personen': ['Wind, Hannes', 'Skolud, Matthias'], 'Institut': 'E253 Institut für Architektur und Entwerfen', 'Leistungsnachweis': '<div><p>-&nbsp;&nbsp; &nbsp;Schriftliche Prüfung<br>-&nbsp;&nbsp; &nbsp;Prüfungsfragen: siehe Register „Unterlagen“ (ab Juni 2022)<br>-&nbsp;&nbsp; &nbsp;Prüfungsdauer: 90 Minuten<br>-&nbsp;&nbsp; &nbsp;Während der Prüfung dürfen keinerlei Hilfsmittel (Schriftstücke, elektronische Geräte, Taschenrechner, Handys, Kopfhörer, etc.) verwendet werden.<br><br><strong>Abmeldung von Prüfungen gem. Mitteilungsblatt 2014, 3. Stück; Nr.22</strong><br>§ 18a. (1) Die Studierenden sind berechtigt, sich bis spätestens zwei Arbeitstage vor dem Prüfungstag mündlich, schriftlich oder elektronisch bei der Prüferin/beim Prüfer oder bei der Studiendekanin/beim Studiendekan von der Prüfung abzumelden.<br>(2) Erscheinen Studierende nicht zu einer Prüfung, ohne sich gemäß Abs. 1 abgemeldet zu haben, so ist die Studiendekanin/der Studiendekan auf Vorschlag der Prüferin/des Prüfers berechtigt, diese Studierenden für einen Zeitraum von acht Wochen von der Anmeldung zu dieser Prüfung auszuschließen. Diese ordnungsrechtliche Frist beginnt mit dem Prüfungstag, an dem die/der Studierende trotz aufrechter Anmeldung ohne vorherige Abmeldung nicht erschienen ist. Die betroffenen Studierenden sind von der Sperre auf geeignete Weise zu informieren. <br>(3) Kann die/der Studierende nachweisen, dass sie/er durch einen triftigen Grund (zB. Unfall) oder einen anderen besonders berücksichtigungswürdigen Grund an einer rechtzeitigen Abmeldung gemäß Abs. 1 gehindert gewesen ist, ist die Sperre aufzuheben.</p>        </div>', 'LVA-Anmeldung': '<table class="standard big">                    <thead>                    <tr>                        <th>Von</th>                        <th>Bis</th>                        <th>Abmeldung bis</th>                    </tr>                    </thead>                    <tbody><tr>                        <td>01.03.2022 08:00                        </td>                        <td>28.02.2023 23:55                        </td>                        <td>28.02.2023 23:55                        </td>                    </tr>                </tbody></table>        <h3>Zulassungsbedingung        </h3>        <p>Voraussetzung für die Anmeldung ist eine Fortmeldung zu einem der folgenden Studien:         </p>        <ul>                <li><a href="/curriculum/public/curriculum.xhtml?key=37047">033 243 Architektur</a>                </li>                <li><a href="/curriculum/public/curriculum.xhtml?key=41934">066 443 Architektur</a>                </li>                <li><a href="/curriculum/public/curriculum.xhtml?key=42323">066 444 Building Science and Environment</a>                </li>        </ul>', 'Curricula': ['033 243 Architektur', ['6. Semester', '<img id="j_id_2o:j_id_e2:j_id_e3:0:precondSteopSteg" src="/course/javax.faces.resource/STEOP_OK.png.xhtml?ln=img" alt="STEOP" style="height: 12pt">', '']], 'Literatur': '<div><p><strong>PRIEBERNIG: KONSTRUIEREN+BAUEN. AVA · TERMINE · KOSTEN · ÖBA, TU Verlag, Wien 2015</strong>, ISBN 978-3-903024-09-0, <a href="http://www.tuverlag.at">www.tuverlag.at</a>, <a href="http://www.grafischeszentrum.com">www.grafischeszentrum.com</a>.<br>Hinweis: Das Buch nimmt Bezug auf das BVergG 2006. In der Vorlesung wird auf die Inhalte des BVergG 2018 eingegangen.</p><p><strong>Skriptum</strong><br><strong>PRIEBERNIG: BAUDURCHFÜHRUNG + AVA 2019</strong>, TU Verlag, Wien 2019, <a href="http://www.tuverlag.at">www.tuverlag.at</a>, <a href="http://www.grafischeszentrum.com">www.grafischeszentrum.com</a>.</p><p>Normen können Sie online an der Bibliothek der TU Wien einsehen (siehe Beschreibung):<br>-&nbsp;&nbsp; &nbsp;ÖN A 2050 Vergabe von Aufträgen über Leistungen - Ausschreibung Angebot Zuschlag.<br>-&nbsp;&nbsp; &nbsp;ÖN A 2060 Allgemeine Vertragsbestimmungen für Leistungen.<br>-&nbsp;&nbsp; &nbsp;ÖN A 2063 Austausch von Leistungsbeschreibungs-, Ausschreibungs-, Angebots-, Auftrags- und Abrechnungsdaten in elektronischer Form.<br>-&nbsp;&nbsp; &nbsp;ÖN B 1801-1 Bauprojekt- und Objektmanagement - Objekterrichtung.<br>-&nbsp;&nbsp; &nbsp;ÖN B 2061 Preisermittlung für Bauleistungen.<br>-&nbsp;&nbsp; &nbsp;ÖN B 2110 Allgemeine Vertragsbestimmungen für Bauleistungen.<br>-&nbsp;&nbsp; &nbsp;ÖN B 2111 Umrechnung veränderlicher Preise von Bauleistungen.<br>-&nbsp;&nbsp; &nbsp;Werkvertragsnormen der Serien ÖN B 22xx, ÖN H 22xx und ÖN D 22xx.<br>-&nbsp;&nbsp; &nbsp;[…]<br>Zugang zur TU-Bibliothek über das Internet des TU-Netzwerks oder über eine <a title="VPN (Virtual Private Network)" href="https://www.it.tuwien.ac.at/services/netzwerkinfrastruktur-und-serverdienste/tunet/vpn-virtual-private-network" target="_blank">VPN-Verbindung</a>:</p><p>Normen (lesen bzw. druck- und speicherbar):<br> _ <a title="https://www.tuwien.at/bibliothek/" href="https://www.tuwien.at/bibliothek/" target="_blank">TU Wien Bibliothek</a><br> _ Normen<br> _ Wo finde ich Normen? (Volltext druck- und speicherbar)<br> _ Ausgewählte ÖNORMEN im PDF-Format über Austrian Standards effects 2.0<br> _ TU Wien Login<br> _ Zustimmung zur Weitergabe persönlicher Daten<br> _ Suche: (z.B. ÖNORM B 2110)<br> <strong>Normen dürfen Sie nicht kopieren!</strong></p><p>Gesetzestexte (lesen bzw. druck- und speicherbar):<br>_ <a title="Rechtsinformationssystem des Bundes" href="https://www.ris.bka.gv.at/" target="_blank">Rechtsinformationssystem des Bundes (RIS)</a><br>_ Bundesrecht<br>_ Bundesrecht konsolidiert<br>_ Suche: (z.B. BVergG)<br>_ Gesamte geltende Rechtsvorschrift für § 0 Bundesvergabegesetz 20xx in neuem Fenster öffnen</p><p>Fachliteratur<br>-&nbsp;&nbsp; &nbsp;Karasek, Georg: Die ÖNORM B 2110, Fassung 15.03.2013, Institut für Zivilrecht, Universität Wien.<br>-&nbsp;&nbsp; &nbsp;Karasek, Georg: ÖNORM B 2110, 3. Aufl., Manz, 2016.<br>-&nbsp;&nbsp; &nbsp;Kropik, Andreas: <a title="Bauvertrags- und Nachtragsmanagement" href="https://www.lindedigital.at/#id:eigen-fb-bauvertr-nachtrag" target="_blank">Bauvertrags- und Nachtragsmanagement</a>, Kropik-Eigenverlag, Perchtoldsdorf, 2014.<br>-&nbsp;&nbsp; &nbsp;Kurz, Thomas: <a title="Vertragsgestaltung im Baurecht " href="https://www.verlagoesterreich.at/vertragsgestaltung-im-baurecht/99.105005-9783704667656" target="_blank">Vertragsgestaltung im Baurecht</a>, Verlag Österreich, Wien, 2015.<br>-&nbsp;&nbsp; &nbsp;Würfele / Bielefeld / Gralla: <a title="Bauobjektüberwachung" href="https://link.springer.com/book/10.1007/978-3-658-10039-1" target="_blank">Bauobjektüberwachung</a>, Springer Vieweg, Wiesbaden, 2017.<br>-&nbsp;&nbsp; &nbsp;Rösel / Busch: <a title="AVA-Handbuch" href="https://link.springer.com/book/10.1007/978-3-658-15053-2" target="_blank">AVA-Handbuch</a> . Ausschreibung - Vergabe - Abrechnung, Springer Vieweg, Wiesbaden, 2017.<br>-&nbsp;&nbsp; &nbsp;Pflaum / Karlberger / Wiener / Opetnik / Rindler / Henseler: <a title=" Handbuch des Ziviltechnikerrechts" href="https://shop.lexisnexis.at/handbuch-des-ziviltechnikerrechts-9783700761570.html" target="_blank">Handbuch des Ziviltechnikerrechts</a>, LexisNexis, Wien, 2015.<br>-&nbsp;&nbsp; &nbsp;S. die Literaturliste in PRIEBERNIG: <a title="KONSTRUIEREN+BAUEN" href="https://shop.tuverlag.at/de/konstruierwnbauen" target="_blank">KONSTRUIEREN+BAUEN</a>. AVA · TERMINE · KOSTEN · ÖBA, TU Verlag, Wien 2015 und in PRIEBERNIG: <a title="BAUDURCHFÜHRUNG + AVA" href="https://shop.tuverlag.at/de/baudurchfuehrung-ava?info=296" target="_blank">BAUDURCHFÜHRUNG + AVA</a>, TU Verlag, Wien 2019.</p><p>Weiterführende Literatur<br>-&nbsp;&nbsp;&nbsp; Bielefeld, Bert: <a title="Basics Terminplanung" href="https://www.degruyter.com/document/doi/10.1515/9783035612646/html" target="_blank">Terminplanung</a>, Birkhäuser Verlag, Basel, 2013.<br>-&nbsp;&nbsp;&nbsp; Becker, Pecco: <a title="Basics Projektsteuerung" href="https://www.degruyter.com/document/doi/10.1515/9783035616934/html" target="_blank">Projektsteuerung</a>, Birkhäuser Verlag, Basel, 2019.<br>-&nbsp;&nbsp;&nbsp; Klein, Hartmut: <a title="Basics Projektplanung" href="https://www.degruyter.com/document/doi/10.1515/9783035612592/html" target="_blank">Projektplanung</a>, Birkhäuser Verlag, Basel, 2013.<br>-&nbsp;&nbsp;&nbsp; Bielefeld,&nbsp;Bert /&nbsp;Schneider, Roland: <a title="Basics Kostenplanung" href="https://www.degruyter.com/document/doi/10.1515/9783035612608/html" target="_blank">Kostenplanung</a>, Birkhäuser Verlag, Basel, 2014.<br>-&nbsp;&nbsp;&nbsp; Bielefeld,&nbsp;Bert: <a title="Basics Bauvertrag" href="https://www.degruyter.com/document/doi/10.1515/9783035615890/html" target="_blank">Bauvertrag</a>, Birkhäuser Verlag, Basel, 2018.<br>-&nbsp;&nbsp;&nbsp; Rusch, Lars-Phillip: <a title="Basics Bauleitung" href="https://www.degruyter.com/document/doi/10.1515/9783035612660/html" target="_blank">Bauleitung</a>, Birkhäuser Verlag, Basel, 2014.<br>-&nbsp;&nbsp;&nbsp; Brandt, Tim / Franssen,&nbsp;Sebastian Th.: <a title="Basics Ausschreibung" href="https://www.degruyter.com/document/doi/10.1515/9783035612653/html" target="_blank">Ausschreibung</a>, Birkhäuser Verlag, Basel, 2014.</p><p>-&nbsp;&nbsp; &nbsp;BVergG - Bundesvergabegesetz.<br>-&nbsp;&nbsp; &nbsp;BauKG - Bauarbeiterkoordinationsgesetz.<br>-&nbsp;&nbsp; &nbsp;ASchG - ArbeitnehmerInnenschutzgesetz.<br>-&nbsp;&nbsp; &nbsp;[…] siehe im Buch und im Skriptum.</p>    </div>        <ul>            <li><a href="/education/course/documents.xhtml?courseNr=253G70&amp;semester=2022S">Zu den Lehrunterlagen</a>            </li>        </ul>', 'Vorkenntnisse': '<div><p><strong>Lehrveranstaltungen des 1. bis 5. Semesters Bachelorstudium Architektur (033 243).</strong></p>        </div>', 'Vorausgehende Lehrveranstaltungen': '<ul>                <li><a href="courseDetails.xhtml?courseNr=253G63">253.G63 VO Hochbau 1</a>                </li>                <li><a href="courseDetails.xhtml?courseNr=253G66">253.G66 VO Hochbau 2</a>                </li>                <li><a href="courseDetails.xhtml?courseNr=253G69">253.G69 VO Hochbau 3</a>                </li>        </ul>', 'Sprache': 'Deutsch'}}



f_runtime_log = pylogs.open_logfile(root_dir + loggin_folder + "runtime_log_" + pylogs.get_time())
sql_insert_courses(test_dat, f_runtime_log)
sys.exit()
















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
	global total_downloaded_files
	global total_page_crawls

	pylogs.write_to_logfile(f_runtime_log, 'processing courses: ' + str(len(acad_course_list)) +
		'| academic program name: ' + academic_program_name)

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
			False
		)

		print("\n\nreturn_info_dict: ")
		#print(*return_info_dict.items(), sep='\n\n')


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
		sql_insert_courses(return_info_dict, pylogs_filepointer)

		# remove the processed entry
		pylogs.write_to_logfile(f_runtime_log, process_course + ' processed -> remove entry')
		acad_course_list.remove(process_course)

		# update the logfile
		f = open(logging_folder + logging_queued_courses, "w")
		for i in range(len(acad_course_list)):
			f.write(acad_course_list[i] + "|" + academic_program_name + "\n")
		f.close()

		print("STOPPP")
		sys.exit()

# logfiles
f_runtime_log = pylogs.open_logfile(root_dir + loggin_folder + "runtime_log_" + pylogs.get_time())
f_runtime_stats = pylogs.open_logfile(root_dir + loggin_folder + "runtime_stats_" + pylogs.get_time())
f_runtime_unknowns = pylogs.open_logfile(root_dir + loggin_folder + "unkown_field_stats_" + pylogs.get_time())

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
	process_courses(acad_course_list, process_acad_prgm_name, f_runtime_log)

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
	process_courses(acad_course_list, process_acad_prgm_name, f_runtime_log)

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
