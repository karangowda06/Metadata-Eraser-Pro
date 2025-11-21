import sys, os, mimetypes, subprocess, json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QTableWidget, QTableWidgetItem, QProgressBar,
    QMessageBox, QComboBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image
from PIL.ExifTags import TAGS
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF for PDF preview

class MetadataEraser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✨ Metadata Eraser Pro ✨")
        self.resize(1100, 650)
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: white; }
            QPushButton {
                background-color: #2e2e2e; color: white; border-radius: 8px; padding: 8px;
            }
            QPushButton:hover { background-color: #444; }
            QComboBox {
                background-color: #2e2e2e; border-radius: 6px; padding: 6px; color: white;
            }
            QTableWidget {
                background-color: #2b2b2b; border-radius: 8px; gridline-color: #444;
            }
            QHeaderView::section {
                background-color: #333; color: white; padding: 4px; border: none;
            }
        """)

        main_layout = QVBoxLayout()

        # --- Top Controls ---
        controls = QHBoxLayout()
        self.file_type = QComboBox()
        self.file_type.addItems(["Image", "PDF", "Video"])
        controls.addWidget(QLabel("File Type:"))
        controls.addWidget(self.file_type)

        upload_btn = QPushButton("📂 Upload File")
        upload_btn.clicked.connect(self.upload_file)
        controls.addWidget(upload_btn)

        erase_btn = QPushButton("🧹 Erase Metadata")
        erase_btn.clicked.connect(self.erase_metadata)
        controls.addWidget(erase_btn)

        main_layout.addLayout(controls)

        # --- Middle Section (Preview left + Metadata right) ---
        middle_layout = QHBoxLayout()

        # Original Preview
        self.original_preview = QLabel("Original Preview")
        self.original_preview.setFixedSize(420, 420)
        self.original_preview.setStyleSheet("border: 2px dashed #555; border-radius: 12px;")
        self.original_preview.setAlignment(Qt.AlignCenter)
        middle_layout.addWidget(self.original_preview)

        # Metadata tables
        right_layout = QVBoxLayout()

        self.meta_before = QTableWidget()
        self.meta_before.setColumnCount(2)
        self.meta_before.setHorizontalHeaderLabels(["Field", "Value"])
        self.meta_before.horizontalHeader().setStretchLastSection(True)

        self.meta_after = QTableWidget()
        self.meta_after.setColumnCount(2)
        self.meta_after.setHorizontalHeaderLabels(["Field", "Value"])
        self.meta_after.horizontalHeader().setStretchLastSection(True)

        right_layout.addWidget(QLabel("🔍 Metadata Before"))
        right_layout.addWidget(self.meta_before)
        right_layout.addWidget(QLabel("✅ Metadata After"))
        right_layout.addWidget(self.meta_after)

        middle_layout.addLayout(right_layout)
        main_layout.addLayout(middle_layout)

        # Cleaned File Preview
        self.cleaned_preview = QLabel("Cleaned File Preview")
        self.cleaned_preview.setFixedSize(420, 220)
        self.cleaned_preview.setStyleSheet("border: 2px dashed #555; border-radius: 12px;")
        self.cleaned_preview.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.cleaned_preview)

        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar { border: 1px solid #555; border-radius: 6px; text-align: center; }
            QProgressBar::chunk { background-color: #00c853; }
        """)
        self.progress.setValue(0)
        main_layout.addWidget(self.progress)

        self.setLayout(main_layout)
        self.file_path = None
        self.output_path = None

    # --- Helpers ---
    def fill_metadata_table(self, table, metadata: dict):
        """Show metadata dict in a QTableWidget"""
        table.setRowCount(0)
        for i, (k, v) in enumerate(metadata.items()):
            table.insertRow(i)
            table.setItem(i, 0, QTableWidgetItem(str(k)))
            table.setItem(i, 1, QTableWidgetItem(str(v)))

    def upload_file(self):
        ftype = self.file_type.currentText()
        file_filter = {
            "Image": "Images (*.jpg *.jpeg *.png *.tiff)",
            "PDF": "PDF Files (*.pdf)",
            "Video": "Video Files (*.mp4 *.mov *.avi *.mkv)"
        }[ftype]

        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", file_filter)
        if not file_path:
            return

        self.file_path = file_path
        self.show_preview(file_path, self.original_preview)
        meta = self.extract_metadata(file_path)
        self.fill_metadata_table(self.meta_before, meta)
        self.meta_after.setRowCount(0)

    def show_preview(self, path, target_label):
        """Preview file in QLabel"""
        mime, _ = mimetypes.guess_type(path)
        if mime and mime.startswith("image"):
            pixmap = QPixmap(path).scaled(400, 400, Qt.KeepAspectRatio)
            target_label.setPixmap(pixmap)
        elif mime == "application/pdf":
            try:
                doc = fitz.open(path)
                page = doc.load_page(0)
                pix = page.get_pixmap()
                img_path = "preview.png"
                pix.save(img_path)
                pixmap = QPixmap(img_path).scaled(400, 400, Qt.KeepAspectRatio)
                target_label.setPixmap(pixmap)
            except:
                target_label.setText("PDF Preview Error")
        elif mime and mime.startswith("video"):
            try:
                thumbnail = "thumb.jpg"
                subprocess.run([
                    "ffmpeg", "-i", path, "-ss", "00:00:01.000", "-vframes", "1", thumbnail, "-y"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                pixmap = QPixmap(thumbnail).scaled(400, 400, Qt.KeepAspectRatio)
                target_label.setPixmap(pixmap)
            except:
                target_label.setText("Video Preview Error")
        else:
            target_label.setText("Preview not available")

    def extract_metadata(self, file_path):
        mime, _ = mimetypes.guess_type(file_path)
        metadata = {}

        if mime and mime.startswith("image"):
            try:
                img = Image.open(file_path)
                # JPEG/TIFF EXIF
                if hasattr(img, "_getexif") and img._getexif():
                    info = img._getexif()
                    for tag, value in info.items():
                        tag_name = TAGS.get(tag, tag)
                        metadata[tag_name] = str(value)
                # PNG info chunks
                if img.format == "PNG" and img.info:
                    metadata.update(img.info)
            except Exception as e:
                metadata["error"] = str(e)

        elif mime == "application/pdf":
            try:
                reader = PdfReader(file_path)
                metadata = dict(reader.metadata)
            except:
                metadata["info"] = "No PDF metadata found."

        elif mime and mime.startswith("video"):
            try:
                result = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", file_path],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                metadata = json.loads(result.stdout).get("format", {}).get("tags", {})
            except:
                metadata["info"] = "No video metadata found."

        return metadata or {"info": "No metadata available"}

    def erase_metadata(self):
        if not self.file_path:
            QMessageBox.warning(self, "No File", "Please upload a file first!")
            return

        base, ext = os.path.splitext(os.path.basename(self.file_path))
        output_dir = os.path.join(os.getcwd(), "CleanedFiles")
        os.makedirs(output_dir, exist_ok=True)
        self.output_path = os.path.join(output_dir, base + "_cleaned" + ext)

        mime, _ = mimetypes.guess_type(self.file_path)

        self.progress.setValue(20)

        if mime and mime.startswith("image"):
            img = Image.open(self.file_path)
            data = list(img.getdata())
            img_no_exif = Image.new(img.mode, img.size)
            img_no_exif.putdata(data)
            img_no_exif.save(self.output_path)

        elif mime == "application/pdf":
            reader = PdfReader(self.file_path)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.add_metadata({})
            with open(self.output_path, "wb") as f:
                writer.write(f)

        elif mime and mime.startswith("video"):
            subprocess.run([
                "ffmpeg", "-i", self.file_path, "-map_metadata", "-1", "-c", "copy", self.output_path, "-y"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        self.progress.setValue(100)

        # Update preview + metadata after cleaning
        self.show_preview(self.output_path, self.cleaned_preview)
        meta_after = self.extract_metadata(self.output_path)
        self.fill_metadata_table(self.meta_after, meta_after)

        QMessageBox.information(self, "Success", "✅ Metadata erased successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MetadataEraser()
    window.show()
    sys.exit(app.exec_())
