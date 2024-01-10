import sys
import os
import qdarkstyle
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog

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

        # Create a button to select directory
        self.select_dir_button = QPushButton("Select Directory")
        self.select_dir_button.clicked.connect(self.select_directory)
        layout.addWidget(self.select_dir_button)

        # Create a search bar
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.file_search)
        layout.addWidget(self.search_bar)

        # Create a table view for search results
        self.search_results = QTableWidget(0, 4)
        self.search_results.setHorizontalHeaderLabels(["Name", "Extension", "Size", "Location"])
        layout.addWidget(self.search_results)

        # Set the default directory to the current directory
        self.directory = '.'

    def select_directory(self):
        self.directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not self.directory:
            self.directory = '.'

    def file_search(self):
        # Clear the table
        self.search_results.setRowCount(0)

        # Get the search term from the search bar
        search_term = self.search_bar.text().lower()

        # Iterate over all files in the selected directory
        for file_name in os.listdir(self.directory):
            # Check if the search term is in the file name
            if search_term in file_name.lower():
                row = self.search_results.rowCount()
                self.search_results.insertRow(row)
                self.search_results.setItem(row, 0, QTableWidgetItem(file_name))
                self.search_results.setItem(row, 1, QTableWidgetItem(os.path.splitext(file_name)[1]))
                self.search_results.setItem(row, 2, QTableWidgetItem(
                    str(os.path.getsize(os.path.join(self.directory, file_name)))))
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
