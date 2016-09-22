import re

def loginMoodle(r, username, password, log):
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
