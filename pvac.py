# THE IDEAS
"""
PVAC - PHOTO VIDEO ARCHIVE CONVERTER
================================================================
Photo Video Archive Converter (PVAC) is a media archiving utility.
It scans the working directory and converts every photo and video
file it finds into a unified format and resolution, making
long-term storage and later playback simpler. Output is
standardized to .webp for photos and .webm for videos, capped at
a maximum resolution of 900px on the shortest side by default.
These formats were chosen for their strong compression efficiency
and comparatively small file size relative to older formats,
while still retaining broad support across modern devices.

Alur Kerja :
----------------------------------------------------------------
1. Recursively scan the working directory for supported photo
   and video files.
2. In each folder, remove leftover temp files from any previous
   interrupted run.
3. Temporarily rename source files with a "conv_" prefix to
   avoid filename collisions during processing.
4. Sort the files naturally, then process each one in order:
   - Already correct format & resolution -> renamed directly.
   - Otherwise -> resized and converted to .webp/.webm.
5. Successfully processed files are renamed to a sequential
   number (0001, 0002, ...); the original source file is then
   deleted.

Requirement :
----------------------------------------------------------------
- Python 3.6+
- pip install ffmpeg-python natsort pillow pillow_heif
- ffmpeg.exe in PATH

Usage :
----------------------------------------------------------------
- python pvac.py


Version : 1.0.0
"""
# IMPORT MODULE
import os
import pathlib
try:
	import ffmpeg
	import natsort
	from PIL import Image, ImageSequence
	from pillow_heif import register_heif_opener
	register_heif_opener()
except ModuleNotFoundError:
	print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Module external not found, try \'\033[32mpip install ffmpeg-python natsort pillow pillow_heif\033[0m\'")
	exit()
# DEFINE GLOBAL VARIABLE
HEADER_BANNER       = """\033[33m
               _ _                                 
   _____ ___ _| |_|___   ___ ___ ___   ___ ___ ___ 
  |     | -_| . | | .'|_| .'|  _|  _|_|  _| . |   |
  |_|_|_|___|___|_|__,|_|__,|_| |___|_|___|___|_|_|
   v1.0.0\033[0m"""
WORKING_PATH        = pathlib.Path('.')
INPUT_PHOTO_FORMAT  = {'.webp', '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.heif', '.heic'}
INPUT_VIDEO_FORMAT  = {'.webm', '.mp4', '.mov',  '.m4v', '.3gp', '.ts',  '.mkv',  '.avi',  '.hevc'}
INPUT_MEDIA_FORMAT  = INPUT_PHOTO_FORMAT | INPUT_VIDEO_FORMAT
MAX_RESOLUTION      = 900 # 1600x900 (HD+)
OUTPUT_PHOTO_FORMAT = '.webp'
OUTPUT_VIDEO_FORMAT = '.webm'
INCONVERT_PREFIX    = 'conv_'
TEMP_FILE_PREFIX    = 'temp_'
# DEFINE FUNCTION
def path_scanner(path):
	scan_result = {}
	try:
		for item in path.rglob('*'):
			if not item.is_file():
				continue
			if not item.suffix.lower() in INPUT_MEDIA_FORMAT:
				continue
			if item.stem.startswith(TEMP_FILE_PREFIX):
				continue
			scan_result.setdefault(item.parent, []).append(item)
		return scan_result
	except PermissionError:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Access denied to : \'\033[32m%s\033[0m\'" % str(path.resolve())[-48:])
		return scan_result
	except Exception as exc:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Internal Python error : %s" % str(exc))
		return scan_result
def photo_converter(input_path, output_path):
	try:
		input_photo = Image.open(input_path)
	except FileNotFoundError:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' not found" % str(input_path)[-48:])
		return 412
	except PermissionError:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' read permission denied" % str(input_path)[-48:])
		return 422
	except OSError:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' corrupt or unreadable" % str(input_path)[-48:])
		return 442
	except Exception as exc:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Internal Python error : %s" % str(exc))
		return 452
	try:
		with input_photo:
			original_width  = input_photo.size[0]
			original_height = input_photo.size[1]
			shortest_side   = min(original_width, original_height)
			if shortest_side <= MAX_RESOLUTION and input_path.suffix.lower() == OUTPUT_PHOTO_FORMAT:
				return 312
			elif shortest_side <= MAX_RESOLUTION:
				new_width  = original_width
				new_height = original_height
			else:
				resize_scale = MAX_RESOLUTION / shortest_side
				new_width    = int(original_width * resize_scale)
				new_height   = int(original_height * resize_scale)
			if getattr(input_photo, 'is_animated', False):
				photo_frame    = []
				photo_duration = []
				for frame in ImageSequence.Iterator(input_photo):
					frame = frame.convert('RGBA').resize((new_width, new_height))
					photo_frame.append(frame)
					photo_duration.append(frame.info.get('duration', 100))
				photo_frame[0].save(output_path, format='WEBP', save_all=True, append_images=photo_frame[1:], duration=photo_duration, loop=input_photo.info.get('loop', 0), disposal=2)
				return 212
			else:
				input_photo.convert('RGBA').resize((new_width, new_height)).save(output_path, format='WEBP')
				return 212
	except AttributeError:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' has no size attribute" % str(input_path)[-48:])
		return 432
	except PermissionError:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' edit permission denied" % str(input_path)[-48:])
		return 422
	except OSError:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' corrupt or unreadable" % str(input_path)[-48:])
		return 442
	except Exception as exc:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Internal Python error : %s" % str(exc))
		return 452
def video_converter(input_path, output_path):
	try:
		probe_video = ffmpeg.probe(str(input_path))
	except FileNotFoundError:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' not found" % str(input_path)[-48:])
		return 412
	except PermissionError:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' read permission denied" % str(input_path)[-48:])
		return 422
	except OSError:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' corrupt or unreadable" % str(input_path)[-48:])
		return 442
	except ffmpeg.Error as error:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m External FFMPEG.EXE error : %s" % str(error))
		return 452
	except Exception as exc:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Internal Python error : %s" % str(exc))
		return 452
	try:
		video_stream = None
		audio_stream = None
		for stream in probe_video['streams']:
			if stream['codec_type'] == 'video' and video_stream is None:
				video_stream = stream
			elif stream['codec_type'] == 'audio' and audio_stream is None:
				audio_stream = stream
		if video_stream is None:
			return 432
		original_width  = int(video_stream['width'])
		original_height = int(video_stream['height'])
		shortest_side   = min(original_width, original_height)
		if shortest_side <= MAX_RESOLUTION and input_path.suffix.lower() == OUTPUT_VIDEO_FORMAT:
			return 312
		elif shortest_side <= MAX_RESOLUTION:
			new_width  = original_width  // 2 * 2
			new_height = original_height // 2 * 2
		else:
			resize_scale = MAX_RESOLUTION / shortest_side
			new_width    = int(original_width * resize_scale)  // 2 * 2
			new_height   = int(original_height * resize_scale) // 2 * 2
		input_stream = ffmpeg.input(str(input_path))
		video        = input_stream.video.filter('scale', new_width, new_height)
		if audio_stream is not None:
			audio = input_stream.audio
			(
				ffmpeg
				.output(video, audio, str(output_path), vcodec='libsvtav1', acodec='libopus', crf=21, preset=4)
				.run(overwrite_output=True, quiet=True)
			)
		else:
			(
				ffmpeg
				.output(video, str(output_path), vcodec='libsvtav1', crf=21, preset=4)
				.run(overwrite_output=True, quiet=True)
			)
		return 212
	except PermissionError:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' read permission denied" % str(input_path)[-48:])
		return 422
	except ffmpeg.Error as error:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m External FFMPEG.EXE error : %s" % str(error))
		return 452
	except Exception as exc:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Internal Python error : %s" % str(exc))
		return 452
def file_renamer(input_path, output_path):
	try:
		input_path.rename(output_path)
		return True
	except Exception as exc:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' Error : %s" % (str(input_path)[-48:], exc))
		return False
def file_controller(list):
	for folder, item, in list.items():
		print("[\033[36m*\033[0m] \033[36mINFO:\033[0m Entering \'\033[32m%s\033[0m\'" % str(folder)[-48:])
		print("--------------------------------")
		for leftover in folder.glob( TEMP_FILE_PREFIX + '*'):
			if leftover.is_file():
				print("[\033[36m*\033[0m] \033[36mINFO:\033[0m \'\033[32m%s\033[0m\'" % str(leftover)[-48:])
				try:
					leftover.unlink()
				except OSError as exc:
					print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Gagal hapus \'\033[32m%s\033[0m\' : %s" % (str(leftover)[-48:], exc))
		prefixed_list = []
		for file in item:
			if file.stem.startswith(INCONVERT_PREFIX):
				prefixed_list.append(file)
			else:
				prefixed_file = file.parent / (INCONVERT_PREFIX + file.stem + file.suffix)
				if not file_renamer(file, prefixed_file):
					continue
				prefixed_list.append(prefixed_file)
		sort_list = natsort.natsorted(prefixed_list, key=lambda sort_item: sort_item.name)
		photo_count = 1
		video_count = 1
		for prefixed_current_file in sort_list:
			if prefixed_current_file.suffix.lower() in INPUT_PHOTO_FORMAT:
				file_type         = 'photo'
				temp_output_path  = folder / (TEMP_FILE_PREFIX + '%04d.webp' % photo_count)
				final_output_path = folder / ('%04d.webp' % photo_count)
				convertion_result = photo_converter(prefixed_current_file, temp_output_path)
			elif prefixed_current_file.suffix.lower() in INPUT_VIDEO_FORMAT:
				file_type         = 'video'
				temp_output_path  = folder / (TEMP_FILE_PREFIX + '%04d.webm' % video_count)
				final_output_path = folder / ('%04d.webm' % video_count)
				convertion_result = video_converter(prefixed_current_file, temp_output_path)
			else:
				continue
			if convertion_result == 212:
				if not file_renamer(temp_output_path, final_output_path):
					continue
				try:
					os.remove(prefixed_current_file)
				except FileNotFoundError:
					print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' not found" % str(prefixed_current_file)[-48:])
					return 412
				except PermissionError:
					print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' read permission denied" % str(prefixed_current_file)[-48:])
					return 422
				except OSError:
					print("[\033[31mX\033[0m] \033[31mERROR:\033[0m File \'\033[32m%s\033[0m\' corrupt or unreadable" % str(prefixed_current_file)[-48:])
					return 442
				except ffmpeg.Error as error:
					print("[\033[31mX\033[0m] \033[31mERROR:\033[0m External FFMPEG.EXE error : %s" % str(error))
					return 452
				except Exception as exc:
					print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Internal Python error : %s" % str(exc))
					return 452
				print("[\033[32m+\033[0m] \'\033[32m%s\033[0m\' --- \'\033[32m%s\033[0m\'" % (str(prefixed_current_file.name)[-48:], str(final_output_path.name)[-48:]))
				if file_type == 'photo':
					photo_count = photo_count + 1
				elif file_type == 'video':
					video_count = video_count + 1				
			elif convertion_result == 312:
				if not file_renamer(prefixed_current_file, final_output_path):
					continue
				print("[\033[32m+\033[0m] \'\033[32m%s\033[0m\' --- \'\033[32m%s\033[0m\'" % (str(prefixed_current_file.name)[-48:], str(final_output_path.name)[-48:]))
				if file_type == 'photo':
					photo_count = photo_count + 1
				elif file_type == 'video':
					video_count = video_count + 1
			else:
				print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Convertion failed (\033[31m%s\033[0m) : \033[32m%s\033[0m" % (convertion_result, str(prefixed_current_file)[-48:]))
				original_name = prefixed_current_file.name[len(INCONVERT_PREFIX):]
				file_renamer(prefixed_current_file, prefixed_current_file.parent / original_name)
				if temp_output_path.exists():
					temp_output_path.unlink()
				break
# MAIN PROGRAM
if __name__ == '__main__':
	try:
		print(HEADER_BANNER)
		print("================================")
		print("[\033[36m*\033[0m] \033[36mINFO:\033[0m Starting Program")
		print("[\033[36m*\033[0m] \033[36mINFO:\033[0m Using configuration:")
		print("\033[36m-\033[0m Working Path   : \'\033[36m%s\033[0m\'" % str(WORKING_PATH.resolve())[-48:])
		print("\033[36m-\033[0m Max Resolution : \033[36m%s\033[0m" % str(MAX_RESOLUTION))
		print("\033[36m-\033[0m Output Format  : \033[36m*%s\033[0m (Photo) & \033[36m*%s\033[0m (Video)" % (OUTPUT_PHOTO_FORMAT, OUTPUT_VIDEO_FORMAT))
		if not WORKING_PATH.exists():
			print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Path \'\033[32m%s\033[0m\' does not exists, exiting program" % str(WORKING_PATH.resolve())[-48:])
			exit()
		if not WORKING_PATH.is_dir():
			print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Path \'\033[32m%s\033[0m\' is invalid, exiting program" % str(WORKING_PATH.resolve())[-48:])
			exit()
		print("[\033[36m*\033[0m] \033[36mINFO:\033[0m Scanning path \'\033[32m%s\033[0m\'" % str(WORKING_PATH.resolve())[-48:])
		scan_result = path_scanner(WORKING_PATH)
		if not scan_result:
			print("[\033[33m>\033[0m] \033[33mSKIP:\033[0m Path \'\033[32m%s\033[0m\' is empty, skiping whole path" % str(WORKING_PATH.resolve())[-48:])
		else:
			file_controller(scan_result)
		print("[\033[36m*\033[0m] \033[36mINFO:\033[0m All operation finish, exiting program")
		exit()
	except KeyboardInterrupt:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Keyboard interrrupt, exiting program")
		exit()
	except Exception as exc:
		print("[\033[31mX\033[0m] \033[31mERROR:\033[0m Internal Python error : %s" % str(exc))
		exit()