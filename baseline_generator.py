import os
import hashlib
import time
import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QFileDialog, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal

def get_file_hash(file_path, algorithm='sha256'):
    """Compute the hash of a file using the specified algorithm."""
    hash_algo = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()

def format_size(size):
    """Format the file size in a human-readable format."""
    original_size = size
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit} ({original_size} B)"
        size /= 1024

def get_file_dates(file_path):
    """Get the creation and modification dates of a file."""
    file_stats = os.stat(file_path)
    creation_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_ctime))
    modification_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime))
    return creation_time, modification_time

def generate_baseline(directory):
    report = []

    for root, dirs, files in os.walk(directory):
        subdir_count = len(dirs)
        file_count = len(files)

        folder_info = f"Folder: {root}\nNumber of subdirectories: {subdir_count}\nNumber of files: {file_count}\n"
        report.append(folder_info)

        report.append("Files:\n")
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            file_hash = get_file_hash(file_path)
            creation_time, modification_time = get_file_dates(file_path)
            file_info = (f"  Name: {file}\n  Size: {format_size(file_size)}\n  Hash: {file_hash}\n"
                         f"  Date Created: {creation_time}\n  Date Modified: {modification_time}\n")
            report.append(file_info)

        if subdir_count > 0:
            report.append("Subdirectories:\n")
            for subdir in dirs:
                subdir_path = os.path.join(root, subdir)
                subdir_info = f"  Name: {subdir}\n  Path: {subdir_path}\n"
                report.append(subdir_info)

        report.append("\n")

    return ''.join(report)

def save_report(report, output_path):
    with open(output_path, 'w') as f:
        f.write(report)

class BaselineWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)

    def __init__(self, directory, output_path):
        super().__init__()
        self.directory = directory
        self.output_path = output_path

    def run(self):
        baseline_report = generate_baseline(self.directory)
        save_report(baseline_report, self.output_path)
        self.finished.emit(self.output_path)

class BaselineGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Baseline Generator")
        self.setGeometry(100, 100, 500, 100)

        layout = QVBoxLayout()

        # Directory selection
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("Select Directory:")
        self.dir_input = QLineEdit()
        self.dir_browse_button = QPushButton("Browse")
        self.dir_browse_button.clicked.connect(self.browse_directory)

        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.dir_browse_button)

        # Output file selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel("Output File Path:")
        self.output_input = QLineEdit()
        self.output_browse_button = QPushButton("Browse")
        self.output_browse_button.clicked.connect(self.browse_output_file)

        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(self.output_browse_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)

        # Generate baseline button
        self.generate_button = QPushButton("Generate Baseline")
        self.generate_button.clicked.connect(self.generate_baseline)

        layout.addLayout(dir_layout)
        layout.addLayout(output_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.generate_button)

        self.setLayout(layout)

    def browse_directory(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder_selected:
            self.dir_input.setText(folder_selected)

    def browse_output_file(self):
        file_selected, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "Text Files (*.txt);;All Files (*)")
        if file_selected:
            self.output_input.setText(file_selected)

    def generate_baseline(self):
        directory = self.dir_input.text()
        output_file = self.output_input.text()

        if not directory:
            QMessageBox.critical(self, "Error", "Please select a directory.")
            return

        if not output_file:
            QMessageBox.critical(self, "Error", "Please select an output file path.")
            return

        self.progress_bar.setVisible(True)
        self.generate_button.setEnabled(False)

        self.worker = BaselineWorker(directory, output_file)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_finished(self, output_file):
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        QMessageBox.information(self, "Success", f"Baseline report saved to {output_file}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BaselineGeneratorApp()
    window.show()
    sys.exit(app.exec())
