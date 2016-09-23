#!/usr/bin/env python

import os
from os.path import isfile, join
from subprocess import run, PIPE
import csv

workingDir = input("working folder: ")
outputFile = join(workingDir, str(int(input("output csv priority (integer, default 50): ") or "50")) + ".csv")

if isfile(outputFile):
	print("Warning: file %s already exists." % outputFile)

student = {}

sid, program = "", ""

while True:
	sid = input("Student Number[%s]: " % sid if sid else "Student Number: ") or sid

	if sid == "exit":
		break

	program = input("Program[%s]: " % program if program else "Program: ") or program
	file = join(join(workingDir, sid), program + ".cpp")
	if isfile(file):
		print("----- Student: %s, Program: %s.cpp" % (sid, program))
		run(["cat", file])
		print("-----")
		comment = input("Any comment? (leave blank to skip this entry) ")
		if comment == "":
			print("Comment skipped.")
			continue
		else:
			comment = "<p>%s</p>" % comment
		if sid in student:
			student[sid] += comment
		else:
			student[sid] = comment
	else:
		print("Cannot find file %s..." % file)

if len(student) > 0:
	with open(outputFile, "w", newline="") as oFile:
		csvWritter = csv.writer(oFile)
		csvWritter.writerow(['sid', 'comment'])
		for sid, comment in student.items():
			csvWritter.writerow([sid, comment])

	print("CSV Written to %s. Total #record = %d." % (outputFile, len(student)))

	os.system("pause")
