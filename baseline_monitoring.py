import os
import hashlib
import time
import random
from datetime import datetime, timedelta
import pytz
from PySide6.QtCore import QThread, Signal

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

def extract_folder_and_file_hashes(baseline):
    folder_names = set()
    file_hashes = {}
    lines = baseline.splitlines()
    
    current_folder = ""
    file_name = ""
    file_path = ""
    
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
            if file_path:  # Ensure file_path is not empty
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

def generate_timestamps(regular_interval, random_checks):
    pakistan_tz = pytz.timezone('Asia/Karachi')
    interval_seconds = 3600 // regular_interval
    regular_timestamps = [datetime.now(pakistan_tz) + timedelta(seconds=i*interval_seconds) for i in range(regular_interval)]
    random_timestamps = []
    min_interval_seconds = 60

    for i in range(regular_interval - 1):
        interval_diff = (regular_timestamps[i + 1] - regular_timestamps[i]).total_seconds()
        selected_times = set()
        while len(selected_times) < random_checks:
            random_time = regular_timestamps[i] + timedelta(seconds=random.uniform(0, interval_diff))
            if all(abs((random_time - rt).total_seconds()) >= min_interval_seconds for rt in selected_times):
                selected_times.add(random_time)
        random_timestamps.extend(selected_times)

    all_timestamps = regular_timestamps + random_timestamps
    all_timestamps.sort()
    return all_timestamps

class BaselineComparisonWorker(QThread):
    finished = Signal(str)

    def __init__(self, baseline_file, directory, output_path, regular_interval, random_checks):
        super().__init__()
        self.baseline_file = baseline_file
        self.directory = directory
        self.output_path = output_path
        self.regular_interval = regular_interval
        self.random_checks = random_checks
        self._running = True

    def run(self):
        with open(self.baseline_file, 'r') as f:
            original_baseline = f.read()

        timestamps = generate_timestamps(self.regular_interval, self.random_checks)
        for timestamp in timestamps:
            if not self._running:
                break
            time_to_wait = (timestamp - datetime.now(pytz.timezone('Asia/Karachi'))).total_seconds()
            if time_to_wait > 0:
                time.sleep(time_to_wait)
            generated_baseline = generate_baseline(self.directory)
            comparison_report = compare_baselines(original_baseline, generated_baseline)
            with open(self.output_path, 'a') as f:
                f.write(comparison_report + '\n\n')

        self.finished.emit(self.output_path)

    def stop(self):
        self._running = False
