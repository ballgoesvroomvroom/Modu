import os
from shutil import copy2
from dotenv import load_dotenv

from moviepy.editor import *

from pytube import YouTube as yt
import dropbox_handler as db

import pyperclip

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from mutagen.easyid3 import EasyID3

import requests

from finput import *
setInputPath("youdownloaderinput.txt")

load_dotenv()
try:
	dump = os.getenv('BIN_PATH')
	if dump == None: raise Exception
except:
	print("Missing BIN_PATH in .env file")

	raise Exception ## dumb but raise error to get out of code

output_file = None
try:
	output_file = os.getenv("OUTPUT_PATH")
	if output_file == None: raise Exception
except:
	print("Continuing without an output file; to add one, assign the path of the output file to the variable 'OUTPUT_PATH' in an .env file")

def getthumbnail(unparsed_link):
	## unparsed_link: https://youtu.be/NkUKg51cgwU
	parsed_link = unparsed_link.split("/")[-1]
	save_to = dump +"/ImageCover.jpg"
	r = requests.get("http://img.youtube.com/vi/{}/0.jpg".format(parsed_link))
	with open(save_to, 'wb') as f:
		f.write(r.content)
	return save_to

def add_coverimage(audiofilepath, imagefilepath):
	# audiofilepath = "test.mp3"
	# imagefilepath = "b.jpg"

	audio = MP3(audiofilepath, ID3 = ID3)

	try:
		audio.add_tags()
	except error:
		print("ERROR")

	audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover (front)',data=open(imagefilepath,'rb').read()))
	audio.save()
	return audiofilepath

def fill_tags(audiofilepath, data):
	"""
	audiofile = "C:/Users/song.mp3"
	data = {
		artist: "song author",
		title: "song title",
		image_cover: "C:/Users/cover.jpg"
	}
	"""
	id3 = EasyID3(audiofilepath)

	for k in data:
		id3[k] = data[k]

	id3.save(audiofilepath)
	return audiofilepath

if __name__ == "__main__":
	print("Running..")

	## pilot code
	while True:
		# db.upload(r"C:\Users\faded\Desktop\Python\downloaderTube\bin\flushed2.png")
		# break
		link = cinput("Video link: ")
		print(link)
		if link == "":
			## get out of loop
			break

		files_to_remove = []

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
		tagNo = cinput("itag no: ")
		while not tagNo.isdigit():
			print("Invalid cinput.\n")
			tagNo = cinput("itag no: ")
		tagNo = int(tagNo)

		path = video.get_by_itag(tagNo).download(dump)

		## prompt user to ask if file needs to be converted to mp3
		promptToConvert = cinput("Convert the file to a .mp3? (y/n)\n").lower()
		if promptToConvert == "y":
			print("Converting to .mp3")

			newPath = path[:len(path) -1] + "3" ## rewrite mp4 path to mp3 path
			clip = VideoFileClip(path)

			audio = clip.audio
			audio.write_audiofile(newPath)
			audio.close()
			clip.close()

			files_to_remove.append(path) ## .mp4 file
			path = newPath

			## ID3 metadata stuff
			print(videoTitle)
			print("\nInputting ID3 tags.")
			true_author = cinput("Artist name: ")
			true_title = cinput("Song name: ")

			## add cover image; modify tag properties
			cover_image = getthumbnail(link) ## returns the path
			path = add_coverimage(path, cover_image) ## returns the same path; added cover image
			files_to_remove.append(cover_image)

			path = fill_tags(path, {"title": true_title, "artist": true_author})

			## rename path based on author and title
			## absolute path
			split_path = path.split("\\")[:-1] ## remove the file name and extension
			new_path = "\\".join(split_path) +("\\{} - {}.mp3".format(true_author, true_title))
			# new_path = "\\".join(split_path) +("\\{}.mp3").format(true_title)
			print("Renaming file from:\n{}\nto:\n{}".format(path, new_path))

			os.rename(path, new_path)
			path = new_path
		else:
			print("Refused to convert, uploading as a .mp4")

		# copy2(path, "C:\\Users\\faded\\Music") ## add this in to save to local file
		link = db.upload(path) ## path = "//home/runner/youdownloader/bin/song.mp3")
		failed = False
		if link == None:
			print("Failed to create.\n")
			print("Downloaded file left untouched.")
			failed = True
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
				with open(output_file, "a", encoding = "utf-8") as f:
				    f.write(path + ":\n" + link + "\n\n")
		files_to_remove.append(path)

		if not failed:
			for i in files_to_remove:
				os.remove(i)
	print("Done; exiting")