import os
import hashlib
import time
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QFileDialog, QMessageBox, QProgressBar, QTabWidget, QMainWindow, QDialog)
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
            file_info = (f"  Name: {file}\n  Path: {file_path}\n  Size: {format_size(file_size)}\n  Hash: {file_hash}\n"
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

def extract_folder_and_file_hashes(baseline):
    folder_names = set()
    file_hashes = {}
    lines = baseline.splitlines()
    
    current_folder = ""
    file_path = ""  # Initialize file_path to an empty string
    for line in lines:
        if line.startswith("Folder: "):
            current_folder = line[8:]
            folder_names.add(current_folder)
        elif line.startswith("  Name: "):
            file_name = line[8:]
        elif line.startswith("  Path: "):
            file_path = line[8:]
        elif line.startswith("  Hash: "):
            file_hash = line[8:]
            file_hashes[file_hash] = file_path
    
    return folder_names, file_hashes

def compare_baselines(original_baseline, generated_baseline):
    """Compare two baselines and generate a comparison report."""
    original_folders, original_hashes = extract_folder_and_file_hashes(original_baseline)
    generated_folders, generated_hashes = extract_folder_and_file_hashes(generated_baseline)

    matched_folders = original_folders.intersection(generated_folders)
    unmatched_folders = generated_folders - original_folders

    matched_hashes = original_hashes.keys() & generated_hashes.keys()
    unmatched_hashes = generated_hashes.keys() - original_hashes.keys()

    total_files = len(matched_hashes) + len(unmatched_hashes)
    total_folders = len(matched_folders) + len(unmatched_folders)
    total_items = total_files + total_folders
    matched_items = len(matched_hashes) + len(matched_folders)

    if total_items > 0:
        matching_percentage = round((matched_items / total_items) * 100)
    else:
        matching_percentage = 100

    comparison_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    report = []
    report.append(f"Comparison time: {comparison_time}")
    report.append(f"No of files matched: {len(matched_hashes)}")
    report.append(f"No of files not matched: {len(unmatched_hashes)}")
    report.append(f"Matching percentage: {matching_percentage}%")

    if unmatched_hashes:
        report.append("\nAdded or modified files:")
        for hash in unmatched_hashes:
            report.append(f"  Path: {generated_hashes[hash]}\n  Hash: {hash}")

    if unmatched_folders:
        report.append("\nAdded or modified directories:")
        for folder in unmatched_folders:
            report.append(f"  Folder: {folder}")

    return '\n'.join(report)

class ComparisonWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)

    def __init__(self, baseline_file, directory, output_path):
        super().__init__()
        self.baseline_file = baseline_file
        self.directory = directory
        self.output_path = output_path

    def run(self):
        with open(self.baseline_file, 'r') as f:
            original_baseline = f.read()

        generated_baseline = generate_baseline(self.directory)
        comparison_report = compare_baselines(original_baseline, generated_baseline)
        save_report(comparison_report, self.output_path)
        self.finished.emit(self.output_path)

class ComparisonWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("One Time Integrity Checking")
        self.setGeometry(100, 100, 500, 200)

        layout = QVBoxLayout()

        # Baseline file selection
        baseline_layout = QHBoxLayout()
        self.baseline_file_label = QLabel("Baseline File:")
        self.baseline_file_input = QLineEdit()
        self.baseline_file_browse_button = QPushButton("Browse")
        self.baseline_file_browse_button.clicked.connect(self.browse_baseline_file)

        baseline_layout.addWidget(self.baseline_file_label)
        baseline_layout.addWidget(self.baseline_file_input)
        baseline_layout.addWidget(self.baseline_file_browse_button)

        # Directory selection
        dir_layout = QHBoxLayout()
        self.compare_dir_label = QLabel("Select Directory to Compare:")
        self.compare_dir_input = QLineEdit()
        self.compare_dir_browse_button = QPushButton("Browse")
        self.compare_dir_browse_button.clicked.connect(self.browse_compare_directory)

        dir_layout.addWidget(self.compare_dir_label)
        dir_layout.addWidget(self.compare_dir_input)
        dir_layout.addWidget(self.compare_dir_browse_button)

        # Output file selection
        output_layout = QHBoxLayout()
        self.compare_output_label = QLabel("Comparison Report Path:")
        self.compare_output_input = QLineEdit()
        self.compare_output_browse_button = QPushButton("Browse")
        self.compare_output_browse_button.clicked.connect(self.browse_compare_output_file)

        output_layout.addWidget(self.compare_output_label)
        output_layout.addWidget(self.compare_output_input)
        output_layout.addWidget(self.compare_output_browse_button)

        # Progress bar
        self.compare_progress_bar = QProgressBar()
        self.compare_progress_bar.setRange(0, 0)
        self.compare_progress_bar.setVisible(False)

        # Compare button
        self.compare_button = QPushButton("Compare")
        self.compare_button.clicked.connect(self.compare_baselines)

        layout.addLayout(baseline_layout)
        layout.addLayout(dir_layout)
        layout.addLayout(output_layout)
        layout.addWidget(self.compare_progress_bar)
        layout.addWidget(self.compare_button)

        self.setLayout(layout)

    def browse_baseline_file(self):
        file_selected, _ = QFileDialog.getOpenFileName(self, "Select Baseline File", "", "Text Files (*.txt);;All Files (*)")
        if file_selected:
            self.baseline_file_input.setText(file_selected)

    def browse_compare_directory(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Directory to Compare")
        if folder_selected:
            self.compare_dir_input.setText(folder_selected)

    def browse_compare_output_file(self):
        file_selected, _ = QFileDialog.getSaveFileName(self, "Save Comparison Report", "", "Text Files (*.txt);;All Files (*)")
        if file_selected:
            self.compare_output_input.setText(file_selected)

    def compare_baselines(self):
        baseline_file = self.baseline_file_input.text()
        directory = self.compare_dir_input.text()
        output_path = self.compare_output_input.text()

        if not all([baseline_file, directory, output_path]):
            QMessageBox.warning(self, "Input Error", "Please provide all inputs!")
            return

        self.compare_button.setEnabled(False)
        self.compare_progress_bar.setVisible(True)

        self.worker = ComparisonWorker(baseline_file, directory, output_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.comparison_finished)
        self.worker.start()

    def update_progress(self, value):
        self.compare_progress_bar.setValue(value)

    def comparison_finished(self, output_path):
        self.compare_button.setEnabled(True)
        self.compare_progress_bar.setVisible(False)
        QMessageBox.information(self, "Comparison Complete", f"Comparison report saved to: {output_path}")

if __name__ == "__main__":
    app = QApplication([])
    window = ComparisonWindow()
    window.show()
    app.exec()
