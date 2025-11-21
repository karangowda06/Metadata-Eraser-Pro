✨ Metadata Eraser Pro

A modern, elegant desktop tool built with PyQt5 that allows users to view, analyze, and completely remove metadata from images, PDFs, and videos.
Includes live preview, before/after comparison, and a sleek dark UI.

🚀 Features
🔍 Metadata Inspection

Displays complete metadata before cleaning

Supports:

EXIF for JPG/JPEG/TIFF

PNG info chunks

PDF metadata

Video metadata via ffprobe

🧹 Metadata Removal

Completely strips metadata from:

Images (saved without EXIF)

PDFs (metadata cleared using PyPDF2)

Videos (ffmpeg -map_metadata -1)

👀 Live Preview

Shows original preview

Shows cleaned output preview

PDF page rendering using PyMuPDF

Video thumbnail extraction using ffmpeg

🖥️ Beautiful UI

Dark mode design

Side-by-side metadata tables

Progress bar

Cleaned file auto-saved in a CleanedFiles folder

📦 Tech Stack

Python 3.x

PyQt5 — GUI

Pillow (PIL) — Image handling

PyPDF2 — PDF metadata removal

PyMuPDF (fitz) — PDF preview

ffmpeg / ffprobe — Video metadata & thumbnail

subprocess, mimetypes — System tasks

📁 Project Structure:
MetadataEraser.py      # Main application (PyQt5 GUI)
CleanedFiles/          # Auto-generated after cleaning files
preview.png            # Temporary PDF preview
thumb.jpg              # Temporary video thumbnail


