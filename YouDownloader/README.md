# YouDownloader
Downloads videos from YouTube using [pytubeX](https://pypi.org/project/pytubeX/) onto local machine.<br />
Featuring the ability to convert files with the `.mp4` extension to the `.mp4` extension using the [MoviePy](https://pypi.org/project/moviepy/) module.<br />
Sends video off to [Dropbox](https://www.dropbox.com).<br />
Which thens creates a download link from Dropbox that can be shared.

## List of dependancies:
This project uses a lot of already created, open-sourced, modules.  
requests - https://pypi.org/project/requests/  
pytubeX - https://pypi.org/project/pytubeX/  
MoviePy - https://pypi.org/project/moviepy/  
Pyperclip - https://pypi.org/project/pyperclip/  

## How to use:
You would need to create an app within [Dropbox API](https://www.dropbox.com/developers/apps/create).<br />
When prompted on what type of access is needed, `App folder` is sufficient.<br />
Give it a name and create.<br />
Over on permissions, enable the scopes needed.<br />
A list of scopes needed:
	- `files.metadata.write`
	- `files.metadata.read`
	- `file.content.write`
	- `file.content.read`
	- `sharing.write`
	- `sharing.read`
	- `file_requests.write`
	- `file_requests.read`

Create a `.env` file into the working directory and have the two variables.
	- `DB_ACCESS_TOKEN`; your own personal access token from the newly created app
	- `BIN_PATH`; directory to store downloaded content temporarily

Run `main.py` and answer/do as prompted by the terminal.<br />
The shareable link is stored in `OUTPUT.txt`

### `DB_ACCESS_TOKEN`
To get your own personal access token, head over to the settings panel of your app.<br />
Scroll down and there should be a section that reads `Generated access token`.<br />
Change `Access token expiration` to `No expiration` for the sake of convenience, unless you want to change the token every now and then.<br />
Hit `Generate` and that is your own personal access token.

### `BIN_PATH`
Just your bin's directory, relative to the current working directory where you ran `main.py`.<br />
The downloaded contents are stored temporarily here, such as `.mp4` directly from YouTube and then `.mp3` when converted to `.mp3`.<br />
The contents are removed from that directory after successful uploads to Dropbox

### Example of the said `.env` file
```
DB_ACCESS_TOKEN = qWyqlsanfdns_EASDFnkkadsf-sadhfjh
BIN_PATH = bin
```
###### Of course, that isn't my actual token, just keyboard smashing.

## Note:
Giving the file a substitute name upon uploading and renaming it to its actual name afterwards is not needed whatsoever, remove it at your own will. :)