#!/usr/bin/env python

import requests
import getpass
import re
import logging
import os
from io import BytesIO
from pyquery import PyQuery as pq
import csv

from moodle import loginMoodle

log = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
		'%(asctime)s %(name)-12s %(levelname)-6s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.INFO)

username = input("HKU Portal username: ")
password = getpass.getpass("HKU Portal password: ")
assignment = int(input("The assignment ID you want to score: "))
submissionCSV = input("Submission CSV filename (sid, grade, comment): ")

def submitGrade(r, assignment, sid, grade, comment, log):
	listHTML = r.get("http://moodle.hku.hk/mod/assign/view.php?id=%d&action=grading" % assignment).text
	d = pq(listHTML)
	url = d(".user%s" % sid).children('.c5 a').attr('href')
	if url == None:
		log.error("Cannot find the row for student #%s" % sid)
		return
	editHTML = r.get(url).text
	d = pq(editHTML)

	formV = {}
	for hinp in d("form.gradeform input[type=hidden]"):
		formV[hinp.attrib['name']] = hinp.attrib['value'] # TODOTODOTODOTODOTODOTODOTODOTODOTODO: send notification
	formV['grade'] = str(grade)
	formV['assignfeedbackcomments_editor[text]'] = comment
	formV['savegrade'] = 'Save changes'
	retHTML = r.post("http://moodle.hku.hk/mod/assign/view.php", data=formV).text
	if retHTML.find('The grade changes were saved') < 0:
		log.error("Submission for student #%s failed..." % sid)
		return
	log.info("Submission for student #%s succeeded!" % sid)

studentInfo = {}

with open(submissionCSV, "r", newline='') as csvFile:
	csvContent = csv.reader(csvFile)
	index = {}
	isFirstRow = True
	for csvRow in csvContent:
		if isFirstRow:
			isFirstRow = False
			for i in range(len(csvRow)):
				index[csvRow[i]] = i
			if index['sid'] == None or index['grade'] == None or index['comment'] == None:
				log.error("Cannot find 'sid', 'grade' or 'comment' in the csv file!")
				quit()
		else:
			sid = csvRow[index['sid']]
			grade = csvRow[index['grade']]
			comment = csvRow[index['comment']]
			if sid in studentInfo:
				log.warn("Student #%s has duplicate rows!! Just keep the first." % sid)
			else:
				studentInfo[sid] = {}
				studentInfo[sid]["grade"] = float(grade)
				studentInfo[sid]["comment"] = comment
				# (studentInfo[sid]["grade"] = float(grade)) if grade != ""
				# studentInfo[sid]["comment"] += ("<p>" + comment + "</p>") if comment != "" else "<p><br></p>"
log.info("All students are processed:")
print(studentInfo)

r = requests.session()
log.info("Moodle login succeeded. Hello " + loginMoodle(r, username, password, log) + "!")

for sid, info in studentInfo.items():
	submitGrade(r, assignment, sid, info['grade'], info['comment'], log)

os.system("pause")
