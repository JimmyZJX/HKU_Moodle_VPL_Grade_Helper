#!/usr/bin/env python

from os import listdir
from os.path import isfile, isdir, join
import logging
import os
from subprocess import run, PIPE
import re
import csv

# The compare function for determin whether identical. Give comments at the same time.
def compare(stuout, stdout):
	if stuout == stdout:
		return (1.0, "Accepted")
	elif stuout + "\n" == stdout:
		return (1.0, "Warning: Last Newline")
	elif re.sub('[ \n]+', " ", stuout + "\n") == re.sub('[ \n]+', " ", stdout):
		return (0.8, "Bad Space Or Newline")
	else:
		return (0, "Wrong Answer")

log = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
		'%(asctime)s %(name)-12s %(levelname)-6s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.INFO)

workingDir = input("working folder: ")
outputFile = join(workingDir, str(int(input("output csv priority (integer, default 10): ") or "10")) + ".csv")
stdDir = join(workingDir, "0")
if not isdir(stdDir):
	log.error("Bad folder: cannot find standard program folder '%s/0/'!" % workingDir)
	quit()

programs = [f[:-4] for f in listdir(stdDir)
	if isfile(join(stdDir, f)) and f.endswith(".cpp")]
stdin, stdout = {}, {}

csvColumns = ['score', 'comment']

# Get the test cases and stdout.
for program in programs:
	stdin[program], stdout[program] = [], []

	inFile = join(stdDir, program + ".in")
	if not isfile(inFile):
		log.error("Bad test for '%s': cannot find test case file '%s'!" % (program, inFile))
		quit()
	script_locals = dict()
	with open(inFile) as f:
		exec(f.read(), dict(), script_locals)
	# execfile(inFile, dict(), script_locals)
	try:
		stdin[program] = script_locals["tests"]
		log.info("Found %d testcases for '%s'" % (len(stdin[program]), program))
	except Exception as e:
		log.error("Test case file '%s' should be written in python format"
			"and output a list variable 'tests'!", e)
		quit()

	csvColumns.append(program)

	# compile and run the sample program.
	try:
		result = run(["g++", join(stdDir, program + ".cpp"), "-o", join(stdDir, program)],
			shell=True, check=True, stdout=PIPE, stderr=PIPE)
		# print(result.stdout)
		# print(result.stderr)
	except Exception as e:
		log.error("Error compiling sample program %s.cpp" % program, e)
		quit()
	try:
		for i, test in enumerate(stdin[program], start=1):
			csvColumns.append(program + "_case#%d" % i)
			out = run(join(stdDir, program), shell=True, check=True, timeout=1000,
				universal_newlines=True, input=test, stdout=PIPE, stderr=PIPE).stdout
			stdout[program].append(out)
	except Exception as e:
		log.error("Sample program cannot run test cases.", e)
		quit()
	log.info("Testcases for '%s' are ready." % program)

print("------ Standard inputs and outputs ------")
print(stdin)
print(stdout)
print("-----------------------------------------")

# Compile students' programs and check output.
student = {} # id -> (program1, program2...)
studentID = [f for f in listdir(workingDir) if isdir(join(workingDir, f)) and f != "0"]

for stuI, sid in enumerate(studentID, 1):
	log.info("Processing student #%s (%d/%d)" % (sid, stuI, len(studentID)))
	studentDir = join(workingDir, sid)
	student[sid] = {}
	student[sid]['score'] = 0.0
	student[sid]['comment'] = ""
	for program in programs:
		# compile
		try:
			run(["g++", join(studentDir, program + ".cpp"), "-o", join(studentDir, program)],
				shell=True, check=True, stdout=PIPE, stderr=PIPE)
		except Exception as e:
			student[sid]['comment'] += "<p>Your `%s` program cannot compile.</p>" % (program)
			student[sid][program] = 0.0
			log.warn("Student %s's program '%s' cannot compile!" % (sid, program))
			continue
		# test
		score = 0.0
		comments = []
		for i, (test, result) in enumerate(zip(stdin[program], stdout[program]), start=1):
			try:
				out = run(join(studentDir, program), shell=True, check=True, timeout=1000,
					universal_newlines=True, input=test, stdout=PIPE, stderr=PIPE).stdout
				student[sid][program + "_case#%d" % i] = repr(out)
				cur_score, cur_comment = compare(out, result)
				score += cur_score
				comments.append(cur_comment)
			except Exception as e:
				log.error("Fail to execute student %s's program '%s' on case %d." % (sid, program, i))
				continue
		student[sid]['comment'] += "<p>Quick feedback for each test case of `%s`: %s</p>" % (program, ", ".join(comments))
		student[sid][program] = score
		student[sid]['score'] += score

# print(student)

with open(outputFile, "w", newline="") as oFile:
	csvWritter = csv.writer(oFile)
	csvWritter.writerow(['sid'] + csvColumns)
	for sid, obj in student.items():
		row = [sid]
		for col in csvColumns:
			row.append(student[sid][col] if col in student[sid] else "")
		csvWritter.writerow(row)

log.info("CSV Written to %s. Total #record = %d." % (outputFile, len(student)))

with open("test.log", "w") as logFile:
	logFile.write(str(student))

os.system("pause")

