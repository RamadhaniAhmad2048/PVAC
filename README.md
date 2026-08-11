# PVAC — Photo Video Archive Converter

Photo Video Archive Converter (PVAC) is a media archiving utility. It scans
the working directory and converts every photo and video file it finds into
a unified format and resolution, making long-term storage and later playback
simpler. Output is standardized to `.webp` for photos and `.webm` for
videos, capped at a maximum resolution of 900px on the shortest side by
default. These formats were chosen for their strong compression efficiency
and comparatively small file size relative to older formats, while still
retaining broad support across modern devices.

## Features

- Recursively processes the working directory and all subdirectories
- Converts photos to `.webp` (including animated images/GIFs)
- Converts videos to `.webm` (AV1 video + Opus audio)
- Resizes media so the shortest side never exceeds `MAX_RESOLUTION`
  (upscaling is never performed)
- Skips files that are already in the correct format and resolution
- Renames processed files into a clean, natural-sorted sequence
  (`0001.webp`, `0002.webp`, `0001.webm`, ...)
- Safe to re-run: already-converted files are left untouched

## How It Works

1. Recursively scan the working directory for supported photo and video
   files.
2. In each folder, remove leftover temp files from any previous
   interrupted run.
3. Temporarily rename source files with a `conv_` prefix to avoid
   filename collisions during processing.
4. Sort the files naturally, then process each one in order:
   - Already correct format & resolution → renamed directly.
   - Otherwise → resized and converted to `.webp` / `.webm`.
5. Successfully processed files are renamed to a sequential number
   (`0001`, `0002`, ...); the original source file is then deleted.

## Supported Input Formats

| Type  | Extensions |
|-------|------------|
| Photo | `.webp` `.jpg` `.jpeg` `.png` `.bmp` `.gif` `.tiff` `.heif` `.heic` |
| Video | `.webm` `.mp4` `.mov` `.m4v` `.3gp` `.ts` `.mkv` `.avi` `.hevc` |

## Requirement

- Python 3.6 or newer
- `pip install ffmpeg-python natsort pillow pillow_heif`
- FFmpeg binary installed separately and available on `PATH`
  (must support the `libsvtav1` and `libopus` encoders)

## Installation

```bash
pip install ffmpeg-python natsort pillow pillow_heif
```

Make sure `ffmpeg` is installed on your system and accessible from the
command line (`ffmpeg -version` should work).

## Usage

Place `pvac.py` inside the folder you want to process, then run:

```bash
python pvac.py
```

The program processes the current directory and all its subdirectories
in place.

> **⚠️ Warning:** Original files are **permanently deleted** after a
> successful conversion. Back up important files before running this
> tool.

## Configuration

All settings are defined as constants near the top of `pvac.py`:

| Constant | Default | Description |
|---|---|---|
| `MAX_RESOLUTION` | `900` | Maximum size (px) of the shortest side |
| `OUTPUT_PHOTO_FORMAT` | `.webp` | Target format for photos |
| `OUTPUT_VIDEO_FORMAT` | `.webm` | Target format for videos |
| `INCONVERT_PREFIX` | `conv_` | Prefix used while a file is being processed |
| `TEMP_FILE_PREFIX` | `temp_` | Prefix used for temporary output files |
| `WORKING_PATH` | `.` (current directory) | Root folder to scan |

## Conversion Result Codes

Internal functions communicate outcomes through numeric codes:

| Code | Meaning |
|---|---|
| `212` | Converted successfully |
| `312` | Skipped — already correct format & resolution |
| `412` | File not found |
| `422` | Permission denied |
| `432` | Corrupt/invalid media (no valid stream, missing size) |
| `442` | File corrupt or unreadable |
| `452` | Internal or FFmpeg error |

## Known Limitations / Roadmap

- Processing is sequential; no multi-threaded/parallel conversion yet
- No CLI arguments — configuration requires editing constants in the script
- No `--dry-run` or "keep original" mode
- Encoder settings (CRF, preset, codec) are fixed in code

## Version

`1.0.0`
