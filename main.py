import sys
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QListWidget, QWidget, QLabel, QStatusBar,
    QTextEdit, QFrame, QFileDialog, QMessageBox, QDialog, QHBoxLayout, QLineEdit, QComboBox, QRadioButton, QButtonGroup
)
from baseline_generator import BaselineGeneratorApp
from compare_baselines import ComparisonWindow
from baseline_monitoring import BaselineComparisonWorker, generate_baseline
from monitoring import DirectoryMonitor as EventDirectoryMonitor

class AddMonitoringTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Monitoring Task")
        self.setGeometry(300, 300, 400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Directory selection
        input_layout = QHBoxLayout()
        self.directory_label = QLabel("Directory:")
        self.directory_input = QLineEdit()
        self.directory_browse_button = QPushButton("Browse")
        self.directory_browse_button.clicked.connect(self.browse_directory)

        input_layout.addWidget(self.directory_label)
        input_layout.addWidget(self.directory_input)
        input_layout.addWidget(self.directory_browse_button)
        layout.addLayout(input_layout)

        # Regular interval selection
        interval_layout = QHBoxLayout()
        self.regular_interval_label = QLabel("Regular Interval (times per hour):")
        self.regular_interval_combo = QComboBox()
        self.regular_interval_combo.addItems([str(i) for i in range(1, 6)])

        interval_layout.addWidget(self.regular_interval_label)
        interval_layout.addWidget(self.regular_interval_combo)
        layout.addLayout(interval_layout)

        # Random checks selection
        checks_layout = QHBoxLayout()
        self.random_checks_label = QLabel("Random Checks (times per interval):")
        self.random_checks_combo = QComboBox()
        self.random_checks_combo.addItems([str(i) for i in range(1, 6)])

        checks_layout.addWidget(self.random_checks_label)
        checks_layout.addWidget(self.random_checks_combo)
        layout.addLayout(checks_layout)

        # Add task button
        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_task)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Monitor")
        if directory:
            self.directory_input.setText(directory)

    def add_task(self):
        directory = self.directory_input.text()
        regular_interval = int(self.regular_interval_combo.currentText())
        random_checks = int(self.random_checks_combo.currentText())

        if not directory:
            QMessageBox.warning(self, "Error", "Please select a directory.")
            return

        # Generate and save baseline
        baseline_file = os.path.join(BASELINE_DIR, f"{os.path.basename(directory)}_baseline.txt")
        baseline_report = generate_baseline(directory)
        with open(baseline_file, 'w') as f:
            f.write(baseline_report)

        # Add monitoring task to parent
        self.parent().add_monitoring_task(directory, baseline_file, regular_interval, random_checks)
        self.accept()

EVENT_LOG_DIR = "C:\\ProgramData\\FIM\\Events Logs"
BASELINE_LOG_DIR = "C:\\ProgramData\\FIM\\Baselines Comparison Reports"
BASELINE_DIR = "C:\\ProgramData\\FIM\\Baselines"

# Ensure the log directories exist
os.makedirs(EVENT_LOG_DIR, exist_ok=True)
os.makedirs(BASELINE_LOG_DIR, exist_ok=True)
os.makedirs(BASELINE_DIR, exist_ok=True)

class FIMWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Integrity Monitor")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.title_label = QLabel("File Integrity Monitor Dashboard", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.main_content = QWidget()
        self.main_layout = QVBoxLayout(self.main_content)

        self.directory_list_panel = QFrame()
        self.directory_list_panel.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.directory_list_layout = QVBoxLayout(self.directory_list_panel)

        self.directory_list_title_label = QLabel("Directories Being Monitored", self)
        self.directory_list_title_label.setStyleSheet("font-weight: bold;")

        self.directory_list = QListWidget()
        self.directory_list.itemClicked.connect(self.show_directory_info)

        self.directory_list_layout.addWidget(self.directory_list_title_label)
        self.directory_list_layout.addWidget(self.directory_list)

        self.main_layout.addWidget(self.directory_list_panel)

        self.control_panel = QFrame()
        self.control_panel.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.control_layout = QVBoxLayout(self.control_panel)

        self.control_title_label = QLabel("Control Panel", self)
        self.control_title_label.setStyleSheet("font-weight: bold;")

        self.add_monitoring_task_button = QPushButton("Add Monitoring Task")
        self.add_monitoring_task_button.clicked.connect(self.open_add_monitoring_task_dialog)
        self.stop_monitoring_button = QPushButton("Stop Monitoring")
        self.stop_monitoring_button.clicked.connect(self.toggle_monitoring_task)
        self.stop_monitoring_button.setVisible(False)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_log)
        self.baseline_generator_button = QPushButton("Baseline Generator")
        self.baseline_generator_button.clicked.connect(self.open_baseline_generator)
        self.one_time_integrity_check_button = QPushButton("One Time Integrity Check")
        self.one_time_integrity_check_button.clicked.connect(self.open_comparison_window)

        self.control_layout.addWidget(self.control_title_label)
        self.control_layout.addWidget(self.add_monitoring_task_button)
        self.control_layout.addWidget(self.stop_monitoring_button)
        self.control_layout.addWidget(self.refresh_button)
        self.control_layout.addWidget(self.baseline_generator_button)
        self.control_layout.addWidget(self.one_time_integrity_check_button)

        self.main_layout.addWidget(self.control_panel)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)

        self.log_display_title_label = QLabel("Log Display", self)
        self.log_display_title_label.setStyleSheet("font-weight: bold;")

        self.radio_group = QButtonGroup(self)
        self.event_log_radio = QRadioButton("Event Log")
        self.event_log_radio.setChecked(True)
        self.baseline_log_radio = QRadioButton("Baseline Comparison Log")
        self.radio_group.addButton(self.event_log_radio)
        self.radio_group.addButton(self.baseline_log_radio)
        self.radio_group.buttonClicked.connect(self.refresh_log)

        radio_layout = QHBoxLayout()
        
        self.main_layout.addWidget(self.log_display_title_label)
        radio_layout.addWidget(self.event_log_radio)
        radio_layout.addWidget(self.baseline_log_radio)

        self.main_layout.addLayout(radio_layout)
        self.main_layout.addWidget(self.log_display)

        self.layout.addWidget(self.main_content)

        self.event_directory_monitors = {}  # To keep track of event-based directory monitors
        self.baseline_monitors = {}  # To keep track of baseline monitoring tasks
        self.current_directory = None
        self.current_log_type = None  # To keep track of the type of log to display

        self.baseline_generator_app = None
        self.comparison_window = None

    def open_add_monitoring_task_dialog(self):
        dialog = AddMonitoringTaskDialog(self)
        dialog.exec()

    def add_monitoring_task(self, directory, baseline_file, regular_interval, random_checks):
        # Start event monitoring
        event_log_file = os.path.join(EVENT_LOG_DIR, f"{os.path.basename(directory)}_event_log.txt")
        event_monitor = EventDirectoryMonitor()
        event_monitor.start_monitoring(directory, event_log_file)
        self.event_directory_monitors[directory] = event_monitor

        # Start baseline comparison monitoring
        comparison_log_file = os.path.join(BASELINE_LOG_DIR, f"{os.path.basename(directory)}_comparison_log.txt")
        baseline_worker = BaselineComparisonWorker(baseline_file, directory, comparison_log_file, regular_interval, random_checks)
        baseline_worker.finished.connect(lambda: self.status_bar.showMessage(f"Finished monitoring {directory}", 5000))
        baseline_worker.start()
        self.baseline_monitors[directory] = baseline_worker

        self.directory_list.addItem(directory)
        self.status_bar.showMessage(f"Started monitoring task for {directory}", 5000)

    def toggle_monitoring_task(self):
        if self.current_directory:
            if self.stop_monitoring_button.text() == "Stop Monitoring":
                self.stop_monitoring()
                self.stop_monitoring_button.setText("Resume Monitoring")
            else:
                self.resume_monitoring()
                self.stop_monitoring_button.setText("Stop Monitoring")

    def stop_monitoring(self):
        if self.current_directory in self.event_directory_monitors:
            self.event_directory_monitors[self.current_directory].stop_monitoring(self.current_directory)
        if self.current_directory in self.baseline_monitors:
            self.baseline_monitors[self.current_directory].terminate()
        self.status_bar.showMessage(f"Stopped monitoring task for {self.current_directory}", 5000)

    def resume_monitoring(self):
        if self.current_directory in self.event_directory_monitors:
            event_log_file = os.path.join(EVENT_LOG_DIR, f"{os.path.basename(self.current_directory)}_event_log.txt")
            self.event_directory_monitors[self.current_directory].start_monitoring(self.current_directory, event_log_file)
        if self.current_directory in self.baseline_monitors:
            self.baseline_monitors[self.current_directory].start()
        self.status_bar.showMessage(f"Resumed monitoring task for {self.current_directory}", 5000)

    def show_directory_info(self, item):
        self.current_directory = item.text()
        self.refresh_log()
        self.stop_monitoring_button.setVisible(True)
        self.stop_monitoring_button.setText("Stop Monitoring")

    def refresh_log(self):
        if self.current_directory:
            if self.event_log_radio.isChecked():
                log_file = os.path.join(EVENT_LOG_DIR, f"{os.path.basename(self.current_directory)}_event_log.txt")
            elif self.baseline_log_radio.isChecked():
                log_file = os.path.join(BASELINE_LOG_DIR, f"{os.path.basename(self.current_directory)}_comparison_log.txt")
            
            if os.path.exists(log_file):
                with open(log_file, 'r') as file:
                    self.log_display.setText(file.read())
            else:
                self.log_display.setText("No logs available for this directory.")
            self.status_bar.showMessage(f"Refreshed log for {self.current_directory}", 5000)

    def open_baseline_generator(self):
        if not self.baseline_generator_app:
            self.baseline_generator_app = BaselineGeneratorApp()
        self.baseline_generator_app.setWindowModality(Qt.ApplicationModal)
        self.baseline_generator_app.show()

    def open_comparison_window(self):
        if not self.comparison_window:
            self.comparison_window = ComparisonWindow()
        self.comparison_window.setWindowModality(Qt.ApplicationModal)
        self.comparison_window.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FIMWindow()
    window.show()
    sys.exit(app.exec())
