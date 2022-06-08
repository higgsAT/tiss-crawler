# set the directories
DIR = src

all:
	python3 $(DIR)/tiss_crawler.py


# option to display the runtime informations upon finishing of the program
time:
	time -p python3 $(DIR)/tiss_crawler.py
