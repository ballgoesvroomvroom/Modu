import os
from dotenv import load_dotenv

import random
import time

import requests

load_dotenv()
try:
	db_token = os.getenv('DB_ACCESS_TOKEN')
except:
	print("Missing DB_ACCESS_TOKEN in .env")
	raise Exception

## https://www.dropbox.com/oauth2/authorize?client_id=<APP_KEY>&response_type=token
## https://content.dropboxapi.com/2/files/upload
auth_session = requests.Session()
auth_session.headers.update({"Authorization": "Bearer %s" %db_token})

upload_session = requests.Session()
upload_session.headers.update({"Authorization": "Bearer %s" %db_token, "Content-Type": "application/octet-stream"})

acc_data = auth_session.post("https://api.dropboxapi.com/2/users/get_current_account").json()

def getFileNameFromPath(path, index = -1):
    ## recrusive function
	h = path[index:]
	if h[0] == "\\" or h[0] == "/":
		return h[1:]
	else:
		return getFileNameFromPath(path, index -1)
def upload(sourcePath):
	## do some parsing of file path
	filename = getFileNameFromPath(sourcePath)

	file_extension = "." +sourcePath.split(".")[len(sourcePath.split(".")) -1]

	path = "/%s" %filename
	print("sourcePath:", sourcePath)
	print("Path:", path)
	if path[0] == path[1] and path[1] == "/":
	    ## path has an extra leading slash causes dropbox api to reject with malformed path error
	    path = path[1:]
	##print("Decoded path:", filename.decode("utf-8"))

	## generate placeholder name since we cant send names with other characters through post method; latin encoding
	t = time.localtime()
	current_time = time.strftime("%H_%M_%S", t)
	e = "videoPlaceholderName"
	for _ in range(10): ## generate psuedo-unique identifier
		e = "%s-%03d" %(e, random.randint(1, 100))
	fakeName = e + "_" + current_time + file_extension
	fakeRoute = "/%s" %fakeName
	print("fakeRoute: %s" %fakeRoute)
	
	## check if file already exists
	header = {
		    'Authorization': 'Bearer %s' %(db_token),
		    'Content-Type': 'application/json'
		}
	print("Scanning through already created links")
	## validates each link if it can be downloaded; returns first list that has allow_download property set to True
	def check(cursor = ""):
		if cursor == "":
			check_payload = ('{"path": "%s", "direct_only": true}' %path).encode('utf-8')
		else:
			check_payload = ('{"cursor": "%s"}' %cursor).encode('utf-8')
		x = requests.post("https://api.dropboxapi.com/2/sharing/list_shared_links", headers = header, data = check_payload)
		if x.status_code == 200:
			data = x.json()
			
			linkExisted = False
			linkFound = False
			for linkObj in data["links"]:
				if linkObj["link_permissions"]["allow_download"]:
					linkExisted = True
					linkFound = linkObj["url"]
					break
			if not linkExisted:
				if data["has_more"]:
					return check(data["cursor"])
				else:
					return [False]
			else:
				return [True, linkFound]
		else:
			return [False, x]
	result = check()
	if result[0]:
		print("Link already existed.")
		link = result[1]
		return link[:len(link) -1] + "1"
	## get payload(params)
	payload = '{"path": "%s","mode": "add","autorename": "false","mute": false,"strict_conflict": false}' %str(path)
	with open(sourcePath, "rb") as f:
		fileData = f
		upload_session.headers.update({'Dropbox-API-Arg': payload})
		header = {
		    'Authorization': 'Bearer %s' %(db_token),
		    'Dropbox-API-Arg': '{"path": "%s","mode": "add","autorename": false,"mute": false,"strict_conflict": false}' %(fakeRoute),
		    'Content-Type': 'application/octet-stream'
		}

		x = requests.post("https://content.dropboxapi.com/2/files/upload", headers = header, data = fileData)##json = payload, data = fileData)
		##xbc = upload_session.post("https://content.dropboxapi.com/2/files/upload", data = fileData)
		## why wont sessions work T~T
		print("Upload request with:", x)
		if x.status_code != 200:
			return

	## rename file to actual name; using the move api
	move_call_payload = ('{"from_path": "%s","to_path": "%s","autorename": false,"allow_ownership_transfer": false}' %(fakeRoute, path)).encode('utf-8')
	header = {
	    'Authorization': 'Bearer %s' %(db_token),
	    'Content-Type': 'application/json'
	}
	x = requests.post("https://api.dropboxapi.com/2/files/move_v2", headers = header, data = move_call_payload)
	print("Move request with:", x)
	if x.status_code == 409:
	    print("Warning: move request was unsuccessful.")
	    print("Status:", x.json())
	elif x.status_code != 200:
		print("Warning: move request was unsuccessful; most likely a conflict within the files involved; continuing work..", x)

	## get share link
	get_sharelink_payload = ('{"path": "%s","settings": {"audience": "public","access": "viewer","requested_visibility": "public","allow_download": true}}' %path).encode('utf-8')
	header = {
	    'Authorization': 'Bearer %s' %(db_token),
	    'Content-Type': 'application/json'
	}
	x = requests.post("https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings", headers = header, data = get_sharelink_payload)
	print("Create share link request with:", x)
	if x.status_code == 200:
		link =	x.json()["url"]
		return link[:len(link) -1] + "1"
	else:
		print("Failed getting the link")
		if x.status_code == 409:
		    print("Additional information:", x.json())