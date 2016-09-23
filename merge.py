#!/usr/bin/env python

import logging
import os
from os import listdir
from os.path import isfile, isdir, join
import csv

log = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
		'%(asctime)s %(name)-12s %(levelname)-6s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.INFO)

workingDir = input("working folder: ")
outputFile = join(workingDir, input("outputFile[final.csv]: ") or "final.csv")

csvFilesRaw = [f[:-4] for f in listdir(workingDir) if isfile(join(workingDir, f)) and f.endswith(".csv")]
csvFilesNum = [int(f) for f in csvFilesRaw if f.isnumeric()]
log.info("Found %d csv files: %s." % (len(csvFilesNum), str(csvFilesNum)))

os.system("pause")

studentInfo = {}

for fNum in csvFilesNum:
	f = join(workingDir, "%d.csv" % fNum)
	with open(f, "r", newline='') as csvFile:
		csvContent = csv.reader(csvFile)
		index = {}
		isFirstRow = True
		for csvRow in csvContent:
			if isFirstRow:
				isFirstRow = False
				for i in range(len(csvRow)):
					index[csvRow[i]] = i
				if index['sid'] == None:
					log.error("Cannot find 'sid' column in the csv file!")
					quit()
			else:
				sid = csvRow[index['sid']]
				grade = csvRow[index['grade']] if 'grade' in index and csvRow[index['grade']] != "" else None
				comment = csvRow[index['comment']] if 'comment' in index and csvRow[index['comment']] != "" else None
				if sid in studentInfo:
					if grade:
						studentInfo[sid]["grade"] = float(grade)
						log.warn("Overriding grade by %s for student #%s" % (f, sid))
					if comment: studentInfo[sid]["comment"] += comment
				else:
					studentInfo[sid] = {}
					if grade:
						studentInfo[sid]["grade"] = float(grade)
					else:
						studentInfo[sid]['grade'] = ""
					if comment:
						studentInfo[sid]["comment"] = comment
					else: 
						studentInfo[sid]['comment'] = ""
					# (studentInfo[sid]["grade"] = float(grade)) if grade != ""
					# studentInfo[sid]["comment"] += ("<p>" + comment + "</p>") if comment != "" else "<p><br></p>"
log.info("All students' info are loaded: Total #=%d" % len(studentInfo))
# print(studentInfo)

with open(outputFile, "w", newline="") as csvFile:
	csvWriter = csv.writer(csvFile)
	csvWriter.writerow(['sid', 'grade', 'comment'])
	for sid, obj in studentInfo.items():
		if sid == "0":
			continue
		csvWriter.writerow([sid, obj['grade'], obj['comment']])

log.info("CSV Written to %s. Total #record = %d." % (outputFile, len(studentInfo)))

os.system("pause")
