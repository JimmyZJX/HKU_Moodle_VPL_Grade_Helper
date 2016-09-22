#!/usr/bin/env python

import requests
import getpass
import re
import logging
import os
import StringIO
import zipfile

log = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
		'%(asctime)s %(name)-24s %(levelname)-6s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.INFO)

username = raw_input("Portal username: ")
password = getpass.getpass("Portal password: ")
vpl = int(raw_input("The VPL you want to grab: "))
raw_input("Warning: grabbing VPL will rewrite EVERYTHING in the destination folder: %d/. Press Enter to Continue." % vpl)

r = requests.session()

def loginMoodle(r):
	loginUrl = "https://hkuportal.hku.hk/cas/servlet/edu.yale.its.tp.cas.servlet.Login";
	redirUrl = "http://moodle.hku.hk/login/index.php?authCAS=CAS"
	formV = {"username": username, "password": password, "x": "0", "y": "0", "service": redirUrl, "keyid": "0"}

	data = r.post(loginUrl, data=formV).text
	try:
		login_redirect_back_url = re.search(r'<a href="(.*)">here</a>', data).group(1)
	except:
		log.error("Your portal account is not accepted by the system.")
		quit()
	# print login_redirect_back_url
	log.info("Portal login succeeded. Redirecting to Moodle...")

	moodleIndex = r.get(login_redirect_back_url).text
	try:
		dispName = re.search(r'<span class="usertext">(.*?)</span>', moodleIndex).group(1)
	except:
		log.error("Moodle does not accept your account?!")
		quit()
	return dispName

log.info("Moodle login succeeded. Hello " + loginMoodle(r) + "!")

def ampurl(url):
	return url.replace('&amp;', '&')

def grabVPL(vpl):
	data = r.get("http://moodle.hku.hk/mod/vpl/views/submissionslist.php?id=%d" % vpl).text
	submissions = re.findall(r'<a href="(http://moodle\.hku\.hk/mod/vpl/forms/submissionview\.php\?id=\d+&amp;userid=(\d+))&amp;inpopup=1">', data)
	log.info("Found %d submission entries for VPL #%d" % (len(submissions), vpl))

	if not os.path.exists(str(vpl)):
		os.makedirs(str(vpl))

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
		z = zipfile.ZipFile(StringIO.StringIO(zip_content.content))
		userPath = "%d/%s" % (vpl, userID)
		if not os.path.exists(userPath):
			os.makedirs(userPath)
		z.extractall(userPath)

		log.info("Processed user #%6s. Totally %3d/%2d zip files extracted." % (userID, i, len(submissions)))

grabVPL(vpl)
