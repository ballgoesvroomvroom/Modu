import time

class const():
	INIT = False
	FILE_NAME = None

class var():
	line = 0

def cinput(s = ""):
	if not const.INIT:
		print("Exiting, initialise with init(file_path)")
		return

	inp = ""
	with open(const.FILE_NAME, "r") as f:
		inp = f.readlines()[var.line]

	var.line += 1

	inp = inp.replace("\n", "")

	print(s +inp)
	time.sleep(1)
	return inp

def setInputPath(file_path):
	if not const.INIT: const.INIT = True
	const.FILE_NAME = file_path

# setInputPath("youdownloaderinput.txt")
# for i in range(1, 25):
# 	cinput("Hello: ")