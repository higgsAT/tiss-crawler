# -*- coding: utf-8 -*-
#!/usr/bin/python3

import mysql.connector as database

# DB login credentials
from config import *

class SqlHandler:
	"""This class handles access to the SQL server (connection, data manipulation, etc.).

	The SQL server can be a local one or a remote one. Various
	different functions for setting up and initiating the
	connection as well as access to the databases and tables
	are provided in this class.
	"""
	def __init__(self):
		"""Define the login credentials for accessing the database.

		The credentials are the username, password and the host
		where the SQL database(s) are located at.
		"""
		print ('creating sqlhandler class object (init)\n')

		# set the login credentials
		self.sql_login_user		= dbLoginUser # loginCredentials.loginData["user"]
		self.sql_login_password	= dbLoginPassword # loginCredentials.loginData["password"]
		self.sql_login_host		= dbHostURL # loginCredentials.loginData["host"]

	def fetch_all_db(self, verbose):
		"""Retrieve / list all existing databases.

		For the given SQL server connection, this function
		returns all databases present. The verbose option
		prints the retrieved information to the terminal.
		"""
		connection = database.connect(
			user = self.sql_login_user,
			password = self.sql_login_password,
			host = self.sql_login_host)
		cursor = connection.cursor(dictionary = True)

		cursor.execute("SHOW DATABASES")
		return_all_db = cursor.fetchall()

		connection.close()

		# print all found databases (to the terminal)
		if verbose == 1:
			for row in return_all_db:
				print (row['Database'])

		return return_all_db

	def fetch_all_tables(self, select_database, verbose):
		"""Retrieve all tables from a given DB on the SQL server.

		For a given database, this function returns all tables
		in this database on the SQL server. The verbose option
		prints the retrieved information to the terminal.
		"""
		connection = database.connect(
			user = self.sql_login_user,
			password = self.sql_login_password,
			host = self.sql_login_host,
			database = select_database)
		cursor = connection.cursor(dictionary = True)

		cursor.execute("SHOW TABLES")
		return_all_tables = cursor.fetchall()

		connection.close()

		if verbose == 1:
			for row in return_all_tables:
				print (row['Tables_in_' + select_database])

		return return_all_tables

	def fetch_table_content(self, select_database, select_table, verbose):
		"""Fetch data from a given table for a selected database and table.

		For a given database and table on a SQL server, this
		function returns all the containing informations
		(e.g., row/column data, etc.). The verbose option
		prints the retrieved information to the terminal.
		"""

		"""
		TODO: change this function so it can only fetch a certain amount of data as well as
		only retrieve the column types ("SHOW COLUMNS ...")
		"""
		connection = database.connect(
			user = self.sql_login_user,
			password = self.sql_login_password,
			host = self.sql_login_host,
			database = select_database)
		cursor = connection.cursor()

		# fetch/print the header (table column names)
		cursor.execute("SHOW COLUMNS FROM " + select_table)
		return_table_header_data = cursor.fetchall()

		if verbose == 1:
			for row in return_table_header_data:
				print(f"{row[0]:>20} ", end = '')
			print('\n---------------------------------------------------')

		# fetch/print the table column data
		cursor.execute("SELECT * FROM " + select_table)
		return_table_contents = cursor.fetchall()

		connection.close()

		if verbose == 1:
			for i in range(len(return_table_contents)):
				print(return_table_contents[i])
				#print(f"{str(return_table_contents[0][i]):>20} ", end = '')

		return return_table_contents, return_table_header_data

	def insert_into_table(self, select_database, insert_statement, insert_data, verbose):
		"""Insert data into a table of a database.

		This functions inserts data (insert_data) into a table
		(defined in the insert statment: insert_data) of a
		database (select_database). The verbose option
		prints the retrieved information to the terminal.
		"""
		connection = database.connect(
			user = self.sql_login_user,
			password = self.sql_login_password,
			host = self.sql_login_host,
			database = select_database)
		cursor = connection.cursor()

		if verbose == 1:
			print("inserting into db: ", select_database,
			": statement: ", insert_statement,
			"; insertdata: ", insert_data)

		cursor.execute(insert_statement, insert_data)
		connection.commit()
		connection.close()

	def create_table(self, select_database, table_name, column_info):
		"""Create a new table.

		With the columns as given by column_info this function
		creates a new table (table_name) in the given database
		(select_database).
		"""
		connection = database.connect(
			user = self.sql_login_user,
			password = self.sql_login_password,
			host = self.sql_login_host,
			database = select_database)
		cursor = connection.cursor()

		# check, whether the table already exists in the DB
		all_tables = self.fetch_all_tables(select_database, 0)
		table_exists = False

		for i in all_tables:
			if i['Tables_in_'+select_database] == table_name:
				print('table', table_name, "already exists in the DB")
				table_exists = True
				break

		if table_exists == False:
			cursor.execute("CREATE TABLE " + table_name + " (" + column_info + ")")

		connection.close()

	def drop_table(self, select_database, delete_table):
		'''This function deletes a table from a selected database.'''
		connection = database.connect(
			user = self.sql_login_user,
			password = self.sql_login_password,
			host = self.sql_login_host,
			database = select_database)
		cursor = connection.cursor()
		sql = "DROP TABLE " + delete_table
		cursor.execute(sql) 
		connection.close()

	def truncate_table(self, select_database, truncate_table):
		"""Clear (truncate) a table.

		For a given table (truncate_table) in the database
		(select_database), this function performes a
		truncation, i.e., all information in the table is
		cleared (truncated).
		"""
		connection = database.connect(
			user = self.sql_login_user,
			password = self.sql_login_password,
			host = self.sql_login_host,
			database = select_database)
		cursor = connection.cursor()
		sql = "TRUNCATE TABLE " + truncate_table
		cursor.execute(sql) 
		connection.close()

	def export_table(self, path, append_only, export_db, export_table):
		"""Export a table from the SQL server to a (local) file on the disk.

		Export a table (into a file on the disk).
		This file can for example be used in phpMyadmin
		to import the table into. The last two arguments
		of this function define the database (export_db)
		and table name (export_table) where the data is
		located which should be exported to the disk. The
		option append_only is used to append to an (external)
		file on the disk. If this variable is set to False,
		a header (CREATE TABLE ...) will be written to the file.
		"""

		# write header information
		file_export_table = open(path, "w")
		file_export_table.write('SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";\n')
		file_export_table.write('START TRANSACTION;\n')
		file_export_table.write('SET time_zone = "+00:00";\n\n')

		# fetch the data
		read_table_data, read_table_header = self.fetch_table_content(export_db, export_table, 0)

		if append_only == False:
			file_export_table.write('CREATE TABLE `' + export_table + '` (\n')

			# replacements to make it compatible using, e.g., phpMyadmin
			replacements = {
				'PRI': 'PRIMARY KEY',
				'YES': '',
				#'None': '',
				'NO': 'NOT NULL'
			}

			# iterate over the list (create and write the data to the file)
			for i in read_table_header:
				# don't end the last line with a comma
				if i != read_table_header[-1]:
					endStr = ','
				else:
					endStr = ''

				# replace certain elements in the list (according to 'replacements')
				i = [replacements.get(x, x) for x in i]

				# remove all elements containing 'None' (in the table header)
				res = [j for j in i if j]

				# create the string
				full_str = ' '.join([str(elem) for elem in res])
				file_export_table.write(full_str + endStr + "\n")

			file_export_table.write(") ENGINE=InnoDB DEFAULT CHARSET=latin1;\n\n")

		# create/write the data
		#
		# HEADER:
		file_export_table.write('INSERT INTO `' + export_table + '` ')

		tmpStr1 = "("

		for add_header_cols in read_table_header:
			tmpStr1 += '`' + add_header_cols[0] + '`, '

		# change the ending of the string
		tmpStr1 = tmpStr1[:-2] + ")"

		file_export_table.write(tmpStr1 + " VALUES \n")

		# DATA (loop through the 'data block'):
		for count, i in enumerate(read_table_data):
			temp_str_data = "("

			for k in i:
				if type(k) == int:
					temp_str_data += "" + str(k) + ", "
				else:
					temp_str_data += "'" + str(k) + "', "

			# change the ending of the string
			temp_str_data = temp_str_data[:-2] + ")"

			if count == len(read_table_data)-1:
				file_export_table.write(temp_str_data + ";\n")
			else:
				file_export_table.write(temp_str_data + ",\n")

		file_export_table.write("\nCOMMIT;")

		file_export_table.close()

	def import_table(self, path, import_target_db):
		"""Import a (local) file into the SQL server.

		This function takes a path to a local SQL file as stated
		by the variable 'path' and inserts it into the database
		provided by the variable 'import_target_db'. This function
		expects for example the following data structure:

		------------------------------------------------------------
		SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
		START TRANSACTION;
		SET time_zone = "+00:00";

		CREATE TABLE `2013__2013_02_28_23_55_21` (
		IP text NOT NULL,
		Date datetime NOT NULL
		) ENGINE=InnoDB DEFAULT CHARSET=latin1;

		INSERT INTO `2013__2013_02_28_23_55_21` (`IP`, `Date`) VALUES 
		('00.111.75.177', '2000-02-01 00:46:30'),
		('66.249.78.123', '2013-02-01 01:14:59'),
		('79.208.109.187', '2013-02-01 01:15:14'),
		('66.249.78.177', '2013-02-01 01:27:57'),
		('77.117.246.38', '2013-02-28 22:31:39'),
		('89.999.179.155', '3121-02-28 23:53:19'),
		('00.111.75.177', '2000-02-01 00:46:30'),
		('66.249.78.123', '2013-02-01 01:14:59'),
		('79.208.109.187', '2013-02-01 01:15:14'),
		('66.249.78.177', '2013-02-01 01:27:57'),
		.
		.
		.

		COMMIT;
		------------------------------------------------------------
		"""
		# open the file; parse it line, by line
		with open(path, encoding = 'utf-8') as fp:
			line = fp.readline()

			while line:
				#print("{}".format(line.strip()))
				line = fp.readline()
				# TODO: IGNORE COMMENTS (lines starting with "/*" or "---"

				# 'CREATE TABLE' block
				if line.find('CREATE TABLE') != -1:
					createTableName = line.split()[2].replace('`', '')
					line = fp.readline()

					# extract column information for the creation of the table
					# e.g.: "`IP` text NOT NULL,`Date` datetime NOT NULL"
					create_table_col_info = []

					while line.find(';') == -1:
						create_table_col_info.append(line.strip())
						line = fp.readline()

					createArgs = ''.join(create_table_col_info)

					# create the table
					self.create_table(import_target_db, createTableName, createArgs)

				# 'INSERT INTO' block
				if line.find('INSERT INTO') != -1:
					import_table_name, returnColumns = self.extract_table_headers(line)

					# create the insert data
					insertColsJoined = ", ".join(returnColumns)

					# create the correct (amount of) placeholders(%s)
					placeholder = "%s"
					placeholder = [placeholder]*len(returnColumns)
					placeholder = ", ".join(placeholder)

					insertStatement = (
						"INSERT INTO " + import_table_name + " (" + insertColsJoined + ") "
						"VALUES (" + placeholder + ")"
					)

					# continue until the last line is reached (marked by the trailing semicolon)
					while line.strip()[-1] != ";":

						line = fp.readline()	# read the next line

						# extract column types (if int -> conversion in the extracted data must be performed
						# to ensure a string is in the tuple which is bein inserted into the db (stored in insertData
						dummyVar, colTypesReturn = self.fetch_table_content(import_target_db, import_table_name, 0)
						column_type = [] # type of columns, e.g., text, datetime, int, etc.
						for var in colTypesReturn:
							column_type.append(var[1])

						insertData = self.extractInsertInformation(line, column_type)

						self.insert_into_table(import_target_db, insertStatement, insertData, 0)

	def determine_endpoint(self, process_str):
		"""Helper function used by extractInsertInformation() to extract data endpoints.

		The function import_table() contains a call to the function
		extractInsertInformation() which calls this function. The
		purpose of this function is to determine the type of element
		endpoints. The overall goal is to read data from the disk and
		insert this into the SQL system. This read data may consist
		of different kind. For example it may look like:
		('0553213695', ...) in which the end of the element is defined
		by a single quotation mark. If may look like:
		(805210407, ...) in which case the end delimiter is a comma.
		This endpoint (delimiter) is used to distinguish between
		elements, i.e., it is used to determine where the next element
		starts and the previous one ended.
		"""

		# first element is a string  -> ('0553213695', ...),
		if process_str == "'":
			end_str = "'"
		# first element is, e.g., a number -> (805210407, ...),
		else:
			end_str = ','

		return end_str

	def extractInsertInformation(self, read_insert_line, column_type):
		"""Used by the function import_table() to read disk data containing SQL info.

		This function takes and processes a single line of the
		read file on the disk containing the SQL statements, e.g.,
		"('79.208.109.187', '2013-02-01 01:15:14'),". USing the
		function determine_endpoint(), these lines are processed,
		i.e., the data fields are extracted. This yields (in the
		former stated example) a tuple containing:
		['79.208.109.187', '2013-02-01 01:15:14']. This tuple is
		then returned from this function.
		"""

		#################################################################################
		# TODO:	o)	fix/check escaped characters, e.g.: aa\",\'`\'\",  \'  ,aa   		#
		#		o)	consider all edge cases, e.g.: "(1, 2, 3, 4, 5, 6),"				#
		#		o)	SQL-terminal dump: "mysqldump -u root -p bookstore > dump.sql"		#
		#		o)	determine type of dump (phpMyAdmin, MariaDB, etc.) since			#
		#			the results look differently (whitespaces, line formatting, etc.	#
		#################################################################################

		return_extracted_data = []

		# remove the round brackets and the trailing comma from the string
		read_insert_line = read_insert_line[1:-3]

		# determine the endpoint for the first element
		end_str = self.determine_endpoint(read_insert_line[0])

		# parse the element (push characters into 'temp_str' and append
		# this string to the list which is returned from this function
		if read_insert_line[0] == "'":
			temp_str = ""
		else:
			temp_str = read_insert_line[0]

		i = 0
		insertPosition = 0

		while i < len(read_insert_line):
			i += 1

			if read_insert_line[i] != end_str:
				temp_str += read_insert_line[i]
			else:
				if (end_str == "'" and read_insert_line[i-1] != "\\") or end_str == ',':
					# if the read string is 'none' it must be converted to an int in case of the table
					# expecting and int as datatype in the DB (else an error is thrown)
					if column_type[insertPosition].find("int") == 0:
						if temp_str == 'None':
							temp_str = None
						else:
							temp_str = int(temp_str)

					return_extracted_data.append(temp_str)
					temp_str = ""
					insertPosition += 1

					if i+1 >= len(read_insert_line):
						break

					# set position to the next element to a whitespace. E.g.,
					# 1) ('00.111.75.177', ...-> skip two to reach a whitespace
					# 2) (0515153, ... -> skip one character reach a whitespace
					#
					# TODO: mysqldump does _not_ add whitespaces between elements:
					# (12,'Jane','Doe','tzu'), and the whole insert statement is a
					# single line (contrary to files generated using phpMyadmin)!
					if end_str == ",":
						i += 1
					if end_str == "'":
						i += 2

					# search the next entry level point
					while read_insert_line[i] == " ":
						i += 1

					# determine next type (endpoints)
					end_str = self.determine_endpoint(read_insert_line[i])

					if end_str == ",":
						temp_str += read_insert_line[i]

		return tuple(return_extracted_data)

	def extract_table_headers(self, read_insert_line):
		"""Used by import_table() this function extracts info from the INSERT INTO line.

		The external SQL files on the disk have a 'header' line
		which may for example look like:
		"INSERT INTO `2013__2013_02_28_23_55_21` (`IP`, `Date`) VALUES".
		This function extracts the table name (2013__2013_02_28_23_55_21)
		and the column names (['IP', 'Date']) in this example. This
		information is stored and returned via the variables 'return_table_name'
		and 'return_columns'.
		"""
		return_table_name = read_insert_line.split('`')[1]

		# cut the string between the round brackets (determine positions)
		bracket_pos_cut_start = read_insert_line.find("(")
		bracket_pos_cut_end = read_insert_line.find(")")

		# extract the column names
		return_columns = read_insert_line[bracket_pos_cut_start+2:bracket_pos_cut_end-1].replace(", `", "").split('`')

		return return_table_name, return_columns
