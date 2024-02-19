import os
import hashlib
import json

def calculate_hash(file_path):
    """
    Calculate the hash of a file.
    """
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

def generate_baseline(folder_path):
    """
    Generate baseline for the selected folder.
    """
    baseline = {}
    for root, dirs, files in os.walk(folder_path):
        folder_info = {}
        file_hashes = {}
        for file in files:
            file_path = os.path.join(root, file)
            file_hashes[file] = calculate_hash(file_path)
        folder_info['file_hashes'] = file_hashes
        baseline[root] = folder_info
    return baseline

def save_baseline(baseline, output_file):
    """
    Save the baseline to a JSON file.
    """
    with open(output_file, 'w') as f:
        json.dump(baseline, f, indent=4)

if __name__ == "__main__":
    folder_path = input("Enter the folder path: ")
    baseline = generate_baseline(folder_path)
    output_file = input("Enter the output file name for baseline: ")
    save_baseline(baseline, output_file)
    print("Baseline generated and saved successfully!")
