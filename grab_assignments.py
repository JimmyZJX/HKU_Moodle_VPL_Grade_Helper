#!/usr/bin/env python

import requests
import getpass
import re
import logging
import os
from io import BytesIO
import zipfile

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
vpls = map(int, input("The VPLs you want to grab, separated by space: ").split())
workingDir = input("working folder: ")

r = requests.session()

log.info("Moodle login succeeded. Hello " + loginMoodle(r, username, password, log) + "!")

def ampurl(url):
	return url.replace('&amp;', '&')

def grabVPL(vpl, workingDir):
	data = r.get("http://moodle.hku.hk/mod/vpl/views/submissionslist.php?id=%d" % vpl).text
	submissions = re.findall(r'<a href="(http://moodle\.hku\.hk/mod/vpl/forms/submissionview\.php\?id=\d+&amp;userid=(\d+))&amp;inpopup=1">', data)
	log.info("Found %d submission entries for VPL #%d" % (len(submissions), vpl))

	if not os.path.exists(workingDir):
		os.makedirs(workingDir)

	i = 0
	for submission in submissions:
		i += 1
		url, userID = submission
		log.debug("Processing user #" + userID + "; " + url)
		subViewData = r.get(ampurl(url)).text

		try:
			subDownloadUrl = re.search(r'<a href="(http://moodle.hku.hk/mod/vpl/views/downloadsubmission\.php\?id=\d+&amp;userid=\d+&amp;submissionid=\d+)">Download</a>', subViewData).group(1)
		except:
			log.info("Student #%d has not submitted any document.")
			continue

		zip_content = r.get(ampurl(subDownloadUrl), stream=True)
		z = zipfile.ZipFile(BytesIO(zip_content.content))
		userPath = "%s/%s" % (workingDir, userID)
		if not os.path.exists(userPath):
			os.makedirs(userPath)
		z.extractall(userPath)

		log.info("Processed user #%6s. Totally %3d/%2d zip files extracted." % (userID, i, len(submissions)))

for vpl in vpls:
	grabVPL(vpl, workingDir)
