#!/usr/bin/python3

from datetime import datetime
import os

class logs:
	'''Class for managing logfiles'''
	def __init__(self, logpath, filename = ''):
		"""Constructor which sets the logging path (logpath).

		The given path sets the path (and filename)
		of the logging file. The filenames of the generated
		logfiles will always consist of the current datestring and
		the optional filename, e.g., "YYYY-MM-DD_HH:MM:SS filename".
		"""

		now_logfile = datetime.now()
		date_logfile = now_logfile.strftime("%Y-%m-%d_%H:%M:%S")

		if (filename != ""):
			spacing = ' '
		else:
			spacing = ''

		# create the filestream
		f = open(logpath + date_logfile + spacing + filename + ".txt", "a")
		self.log_file = f

	def append_to_log(self, msg):
		"""Push a message to the logfile.

		The given string (msg) will be appended to the file and
		the streambuffer is then flushed so that the message
		can be accessed via the file while the program is running.
		Every entry consists of a datestring follwing the message, 
		e.g., "YYYY-MM-DD_HH:MM:SS >> msg". This function is
		suggested for shorter (one-line) messages.
		"""

		# datetime object containing current date and time
		now = datetime.now()

		# create the datestring dd/mm/YY H:M:S
		dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
		print("date and time =", dt_string)

		# write the message the the file and flush the cache
		self.log_file.write(dt_string + " >> " + msg + "\n")
		self.log_file.flush()
		os.fsync()

	def dump_to_log(self, msg, header = ''):
		"""Dump a textblob into the logfile.
		
		Followed by a header (consisting of the current
		date, time and the (optional) variable *header*)
		the message (msg) is written to the logfile. This
		function is intended for pushing larger textblobs
		into the log. Additionally, the textbuffer is flushed
		upon writing at the end of this function.		
		"""

		# datetime object containing current date and time
		now = datetime.now()

		# create the datestring dd/mm/YY H:M:S
		dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
		print("date and time =", dt_string)

		# write the message the the file and flush the cache
		self.log_file.write(dt_string + " >> " + header + "\n\n" + msg)
		self.log_file.flush()
