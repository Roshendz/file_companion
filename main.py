import sys
import os
import subprocess
import platform
import qdarkstyle
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, \
    QPushButton, QFileDialog, QHBoxLayout, QComboBox, QDateTimeEdit, QStyle, QLabel
from datetime import datetime

class FileCompanion(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Companion")
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.setGeometry(100, 100, 800, 600)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create a vertical layout
        layout = QVBoxLayout()
        wid.setLayout(layout)

        # Create a horizontal layout for the select directory button, search bar, and extension dropdown
        hlayout = QHBoxLayout()
        layout.addLayout(hlayout)

        # Create a button to select directory
        self.select_dir_button = QPushButton("Select Directory")
        # Use a standard system icon for the select directory button
        self.select_dir_button.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.select_dir_button.setToolTip('Click this button to select a directory to search')
        self.select_dir_button.clicked.connect(self.select_directory)
        hlayout.addWidget(self.select_dir_button)

        # Create a search bar
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.file_search)
        self.search_bar.setToolTip('Enter a search term to find files')
        hlayout.addWidget(self.search_bar)

        # Create a dropdown list for file extensions
        self.extension_dropdown = QComboBox()
        self.extension_dropdown.addItem("All Files")
        self.extension_dropdown.addItem(".txt")
        self.extension_dropdown.addItem(".png")
        self.extension_dropdown.addItem(".jpg")
        self.extension_dropdown.addItem(".pdf")
        self.extension_dropdown.addItem(".docx")
        # Add more extensions as needed
        self.extension_dropdown.setToolTip('Select a file extension to filter the files')
        hlayout.addWidget(self.extension_dropdown)

        self.start_date_edit = QDateTimeEdit()
        self.start_date_edit.setDateTime(QDateTime.currentDateTime())
        self.start_date_edit.setToolTip('Select the start date for the date range')
        hlayout.addWidget(self.start_date_edit)

        self.end_date_edit = QDateTimeEdit()
        self.end_date_edit.setDateTime(QDateTime.currentDateTime())
        self.end_date_edit.setToolTip('Select the end date for the date range')
        hlayout.addWidget(self.end_date_edit)

        # Create a table view for search results
        self.search_results = QTableWidget(0, 6)
        self.search_results.setHorizontalHeaderLabels(["Name", "Extension", "Size (KB/MB)", "Location", "Creation Date", "Modification Date"])
        # Connect the itemDoubleClicked signal to the open_file method
        self.search_results.itemDoubleClicked.connect(self.open_file)
        layout.addWidget(self.search_results)

        self.file_count_label = QLabel()
        layout.addWidget(self.file_count_label)

        # Set the default directory to the current directory
        self.directory = '.'

    def select_directory(self):
        self.directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not self.directory:
            self.directory = '.'
        # Display all files in the selected directory
        self.display_files()

    def display_files(self):
        # Clear the table
        self.search_results.setRowCount(0)

        # Iterate over all files in the selected directory
        for file_name in os.listdir(self.directory):
            row = self.search_results.rowCount()
            self.search_results.insertRow(row)
            self.search_results.setItem(row, 0, QTableWidgetItem(file_name))
            self.search_results.setItem(row, 1, QTableWidgetItem(os.path.splitext(file_name)[1]))
            file_size = os.path.getsize(os.path.join(self.directory, file_name)) / 1024  # Size in KB
            if file_size > 1024:  # If size > 1024 KB, convert it to MB
                file_size = file_size / 1024
                self.search_results.setItem(row, 2, QTableWidgetItem(f"{file_size:.2f} MB"))
            else:
                self.search_results.setItem(row, 2, QTableWidgetItem(f"{file_size:.2f} KB"))
            self.search_results.setItem(row, 3, QTableWidgetItem(os.path.join(self.directory, file_name)))
            creation_date = datetime.fromtimestamp(os.path.getctime(os.path.join(self.directory, file_name))).strftime(
                '%Y-%m-%d %H:%M:%S')
            self.search_results.setItem(row, 4, QTableWidgetItem(creation_date))
            modification_date = datetime.fromtimestamp(
                os.path.getmtime(os.path.join(self.directory, file_name))).strftime('%Y-%m-%d %H:%M:%S')
            self.search_results.setItem(row, 5, QTableWidgetItem(modification_date))

        self.file_count_label.setText(f"Total Files: {self.search_results.rowCount()}")

    def file_search(self):
        # Get the search term from the search bar
        search_term = self.search_bar.text().lower()

        # Get the selected extension from the dropdown
        selected_extension = self.extension_dropdown.currentText()

        # Get the selected date range from the date edits
        start_date = self.start_date_edit.dateTime().toPyDateTime().timestamp()
        end_date = self.end_date_edit.dateTime().toPyDateTime().timestamp()

        # Clear the table
        self.search_results.setRowCount(0)

        # Iterate over all files in the selected directory
        for file_name in os.listdir(self.directory):
            # Get the file's creation and modification dates
            creation_date = os.path.getctime(os.path.join(self.directory, file_name))
            modification_date = os.path.getmtime(os.path.join(self.directory, file_name))

            # Check if the search term is in the file name, the file has the selected extension, and the creation and modification dates are within the selected range
            if (search_term in file_name.lower() and (selected_extension == "All Files" or os.path.splitext(file_name)[1] == selected_extension) and
                    start_date <= creation_date <= end_date and start_date <= modification_date <= end_date):
                # Get the file size
                file_size = os.path.getsize(os.path.join(self.directory, file_name)) / 1024  # Size in KB
                if file_size > 1024:  # If size > 1024 KB, convert it to MB
                    file_size = file_size / 1024
                    size_str = f"{file_size:.2f} MB"
                else:
                    size_str = f"{file_size:.2f} KB"

                # Add the file to the search results
                row = self.search_results.rowCount()
                self.search_results.insertRow(row)
                self.search_results.setItem(row, 0, QTableWidgetItem(file_name))
                self.search_results.setItem(row, 1, QTableWidgetItem(os.path.splitext(file_name)[1]))
                self.search_results.setItem(row, 2, QTableWidgetItem(size_str))
                self.search_results.setItem(row, 3, QTableWidgetItem(os.path.join(self.directory, file_name)))
                self.search_results.setItem(row, 4, QTableWidgetItem(
                    datetime.fromtimestamp(creation_date).strftime('%Y-%m-%d %H:%M:%S')))
                self.search_results.setItem(row, 5, QTableWidgetItem(
                    datetime.fromtimestamp(modification_date).strftime('%Y-%m-%d %H:%M:%S')))

        self.file_count_label.setText(f"Loaded Files: {self.search_results.rowCount()}")

    def open_file(self, item):
        # Get the file path from the item's row
        file_path = self.search_results.item(item.row(), 3).text()

        # Check if the file path is a directory
        if os.path.isdir(file_path):
            # Open the directory with the default file explorer
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', file_path))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(file_path)
            else:  # linux variants
                subprocess.call(('xdg-open', file_path))
        else:
            # Open the file with the default application
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', file_path))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(file_path)
            else:  # linux variants
                subprocess.call(('xdg-open', file_path))

def main():
    app = QApplication(sys.argv)
    # Apply QDarkStyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    mainWin = FileCompanion()
    mainWin.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
