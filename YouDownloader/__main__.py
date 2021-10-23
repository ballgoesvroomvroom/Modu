import os
from dotenv import load_dotenv

from moviepy.editor import *

from pytube import YouTube as yt
import dropbox_handler as db

import pyperclip

load_dotenv()
try:
	dump = os.getenv('BIN_PATH')
except:
	print("Missing BIN_PATH in .env file")
	raise Exception
output_file = None
try:
	output_file = os.getenv("OUTPUT_PATH")
except:
	print("Continuing without an output file; to add one, assign the path of the output file to the variable 'OUTPUT_PATH' in an .env file")

if __name__ == "__main__":
	print("Running..")

	## pilot code
	while True:
		# db.upload(r"C:\Users\faded\Desktop\Python\downloaderTube\bin\flushed2.png")
		# break
		try:
			link = input("Video link: ")
			if link == "":
				break
		except:
			print("Invalid input.\n")
			continue

		video = yt(link)
		videoTitle = video.title
		videoAuthor = video.author
		print("Video's title:", videoTitle)
		print("Video's author:", videoAuthor)
		video = video.streams.filter(file_extension = "mp4")

		## displays list of streams available to user
		print("")
		for x in video:
			print(x)
			# print("{:<4} {:<10} {:<8} {}".format(x.itag, x.mime_type, x.abr, x.fps))

		## get itag user wants
		tagNo = input("itag no: ")
		while not tagNo.isdigit():
			print("Invalid input.\n")
			tagNo = input("itag no: ")
		tagNo = int(tagNo)

		path = video.get_by_itag(tagNo).download(dump)

		## prompt user to ask if file needs to be converted to mp3
		promptToConvert = input("Convert the file to a .mp3? (y/n)\n").lower()
		if promptToConvert == "y":
			print("Converting to .mp3")

			newPath = path[:len(path) -1] + "3" ## rewrite mp4 path to mp3 path
			clip = VideoFileClip(path)

			audio = clip.audio
			audio.write_audiofile(newPath)
			audio.close()
			clip.close()

			os.remove(path)
			path = newPath
		else:
			print("Refused to convert, uploading as a .mp4")

		link = db.upload(path)##"//home/runner/youdownloader/bin/王優秀 - 始終如一「我的心不聽話總是在想你，總是期待著你回頭的驚喜。」王优秀【動態歌詞/Pinyin Lyrics】.mp3")
		if link == None:
			print("Failed to create.\n")
		else:
			endStr = "\n"
			try:
				pyperclip.copy(link)
				endStr += "(Copied to clipboard)\n"
			except:
				pass
			print(link + endStr)

			if output_file != None:
				print("Full link is in {}\n".format(output_file))
				with open(output_file, "w", encoding = "utf-8") as f:
				    f.write(videoTitle + " - " + videoAuthor + ":\n" + link + "\n\n")
		os.remove(path)