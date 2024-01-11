import sys
import os
import qdarkstyle
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, \
    QPushButton, QFileDialog, QHBoxLayout, QComboBox


class FileCompanion(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Companion")
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
        self.select_dir_button.clicked.connect(self.select_directory)
        hlayout.addWidget(self.select_dir_button)

        # Create a search bar
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.file_search)
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
        hlayout.addWidget(self.extension_dropdown)

        # Create a table view for search results
        self.search_results = QTableWidget(0, 4)
        self.search_results.setHorizontalHeaderLabels(["Name", "Extension", "Size (KB)", "Location"])
        layout.addWidget(self.search_results)

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
            self.search_results.setItem(row, 2, QTableWidgetItem(
                str(os.path.getsize(os.path.join(self.directory, file_name)) / 1024)))
            self.search_results.setItem(row, 3, QTableWidgetItem(os.path.join(self.directory, file_name)))

    def file_search(self):
        # Get the search term from the search bar
        search_term = self.search_bar.text().lower()

        # Get the selected extension from the dropdown
        selected_extension = self.extension_dropdown.currentText()

        # Clear the table
        self.search_results.setRowCount(0)

        # Get the search term from the search bar
        search_term = self.search_bar.text().lower()

        # Iterate over all files in the selected directory
        for file_name in os.listdir(self.directory):
            # Check if the search term is in the file name and the file has the selected extension
            if search_term in file_name.lower() and (
                    selected_extension == "All Files" or os.path.splitext(file_name)[1] == selected_extension):
                row = self.search_results.rowCount()
                self.search_results.insertRow(row)
                self.search_results.setItem(row, 0, QTableWidgetItem(file_name))
                self.search_results.setItem(row, 1, QTableWidgetItem(os.path.splitext(file_name)[1]))
                self.search_results.setItem(row, 2, QTableWidgetItem(
                    str(os.path.getsize(os.path.join(self.directory, file_name)) / 1024)))
                self.search_results.setItem(row, 3, QTableWidgetItem(os.path.join(self.directory, file_name)))

def main():
    app = QApplication(sys.argv)
    # Apply QDarkStyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    mainWin = FileCompanion()
    mainWin.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
