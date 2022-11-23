#!/usr/bin/python3

from datetime import datetime
import os

"""
Routines in this file will manage aggregation of information during
runtime. These consist of
1) source code of crawled pages
2) logging files (crawled pages, downloaded files, etc. with the
corresponding timestamp)
3) files containing the current state of crawling.

For each crawl, files in 1) will be stored in an own folder. Each program
run will have at least one file for 2) and the loggin for 3) the files
will represent the program structure (academic list and courses). Regarding
3), when a part (academic program or course) is finished, the corresponding
entry will be removed from the logfile which ensures continuation from the
correct point in case the program gets interrupted.
"""

def get_time():
	'''Returns the current time formatted in '%Y-%m-%d_%H:%M:%S'''
	now_logfile = datetime.now()
	date_logfile = now_logfile.strftime("%Y-%m-%d_%H:%M:%S")
	return date_logfile

def open_logfile(logfile_file_path):
	'''opens a logfile with the given path and returns the file_pointer'''
	f = open(logfile_file_path + ".log", "a")
	return f

def write_to_logfile(file_pointer, log_message):
		'''writes (append) a meassge into a given logfile'''

		time_now = get_time()

		print(log_message)
		file_pointer.write(time_now + " >> " + log_message + "\n")
		file_pointer.flush()
		os.fsync(file_pointer)

def dump_to_log(logfile_file_path, log_message):
	'''dump a log message into a logfile and close the file'''

	filename_too_long = True

	# shorten the filename until no OSError (filename too long) occurs
	while filename_too_long == True:
		try:
		    f = open(logfile_file_path, "w")
		except OSError as exc:
		    if exc.errno == 36:
		        logfile_file_path = logfile_file_path[:-5] + "..."
		else:
			filename_too_long = False

	f.write(log_message)
	f.close()

def close_logfile(file_pointer):
	'''close a logfile properly'''
	write_to_logfile(file_pointer, "closing log: " + os.path.basename(file_pointer.name))
	file_pointer.close()
