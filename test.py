#!/usr/bin/env python

from os import listdir
from os.path import isfile, isdir, join
import logging
import os
from subprocess import run, PIPE
import re

# The compare function for determin whether identical.
def compare(stuout, stdout):
	stuout = re.sub('[ \n]+', " ", stuout)
	stdout = re.sub('[ \n]+', " ", stuout)
	return stuout == stdout

log = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
		'%(asctime)s %(name)-12s %(levelname)-6s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.INFO)

workingDir = input("working folder: ")
stdDir = join(workingDir, "0")
if not isdir(stdDir):
	log.error("Bad folder: cannot find standard program folder '%s/0/'!" % workingDir)
	quit()

programs = [f[:-4] for f in listdir(stdDir)
	if isfile(join(stdDir, f)) and f.endswith(".cpp")]
stdin, stdout = {}, {}

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
		for test in stdin[program]:
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

i = 0
for sid in studentID:
	i += 1
	log.info("Processing student #%s (%d/%d)" % (sid, i, len(studentID)))
	studentDir = join(workingDir, sid)
	student[sid] = {}
	for program in programs:
		# compile
		try:
			run(["g++", join(studentDir, program + ".cpp"), "-o", join(studentDir, program)],
				shell=True, check=True, stdout=PIPE, stderr=PIPE)
		except Exception as e:
			log.warn("Student %s's program '%s' cannot compile!" % (sid, program))
			student[sid][program] = "Cannot compile."
			continue
		# test
		succ_cnt = 0
		for test, result in zip(stdin[program], stdout[program]):
			try:
				out = run(join(studentDir, program), shell=True, check=True, timeout=1000,
					universal_newlines=True, input=test, stdout=PIPE, stderr=PIPE).stdout
				if compare(out, result):
					succ_cnt += 1
			except Exception as e:
				log.warn("Fail to execute student %s's program '%s'." % (sid, program))
				continue
		student[sid][program] = succ_cnt

print(student)

os.system("pause")

