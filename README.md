# 📁 File Integrity Monitor (FIM)

## 📌 Project Overview

The **File Integrity Monitor (FIM)** is a cybersecurity tool developed in **Python** that monitors directories to detect unauthorized file changes.

The system provides:

* ✅ Real-time directory monitoring
* ✅ Event logging system
* ✅ Baseline comparison reports
* ✅ One-time integrity verification feature
* ✅ Interval-based monitoring

This project demonstrates practical implementation of file hashing, directory scanning, and integrity verification techniques used in cybersecurity.

---

## 🎯 Key Features

### 🔄 1. Real-Time Directory Monitoring

* Continuously monitors a selected directory
* Detects:

  * File modification
  * File deletion
  * File creation
* Generates proper event logs
* Allows interval-based scanning
* Compares files with stored baseline
* Produces comparison reports

---

### 🛡️ 2. One-Time Integrity Check

* Creates a baseline of a selected directory
* Stores file hash values
* Allows future comparison at any time
* Detects:

  * Modified files
  * Missing files
  * Newly added files
* Generates integrity verification report

---

## 🛠️ Technologies Used

* **Programming Language:** Python
* **Hashing Algorithm:** SHA-256
* **File Handling:** Python OS module
* **Logging System:** Python logging module
* **Environment:** Windows / Linux

---

## ⚙️ System Architecture

```
+----------------------+
|  User Input Module   |
+----------------------+
            |
            v
+----------------------+
| Directory Scanner    |
+----------------------+
            |
            v
+----------------------+
| Hash Generator       |
| (SHA-256)            |
+----------------------+
            |
            v
+----------------------+
| Baseline Storage     |
+----------------------+
            |
            v
+----------------------+
| Comparison Engine    |
+----------------------+
            |
            v
+----------------------+
| Logs & Reports       |
+----------------------+
```

---

## 🔍 How the System Works

### 📌 Real-Time Monitoring Process

1. User selects a directory.
2. Baseline is created (if not already present).
3. System scans directory at defined intervals.
4. Current hashes are compared with baseline.
5. Any changes trigger:

   * Log entry
   * Report update

---

### 📌 One-Time Integrity Check Process

1. User selects directory.
2. Baseline hashes are generated and saved.
3. Later, user runs integrity check.
4. System compares:

   * Old baseline
   * Current directory state
5. Detailed comparison report is generated.

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/file-integrity-monitor.git
```

### 2️⃣ Navigate to Project Folder

```bash
cd file-integrity-monitor
```

### 3️⃣ Run the Application

```bash
python main.py
```

*(Ensure Python 3.x is installed on your system.)*

---

## 🧪 Testing Scenarios

To test the system:

* Modify a file inside monitored directory
* Delete a file
* Add a new file
* Run integrity check
* Observe logs and generated reports

---

## 📊 Output Reports Include

* List of modified files
* List of deleted files
* List of newly created files
* Timestamp of scan
* Summary of integrity status

---

## 🔐 Security Implementation

* SHA-256 hashing ensures strong integrity verification
* Secure baseline comparison
* Timestamped logging
* Controlled scan intervals

---

## 🌟 Future Enhancements

* Email alert system
* GUI-based interface
* Database integration
* Real-time notification system
* Cloud-based baseline storage

