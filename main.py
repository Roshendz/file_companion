import hashlib
import shutil
import sys
import os
import subprocess
import platform
import qdarkstyle
from PyQt5.QtCore import QDateTime
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, \
    QPushButton, QFileDialog, QHBoxLayout, QComboBox, QDateTimeEdit, QStyle, QLabel, QMenu, QAction, QCheckBox, \
    QInputDialog, QMessageBox
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

        # Create a checkbox to toggle between all files and duplicate files
        self.toggle_duplicates = QCheckBox("Show only duplicates")
        self.toggle_duplicates.stateChanged.connect(self.display_files)

        # Create a button for creating folders
        self.create_folder_button = QPushButton("Create Folder", self)
        self.create_folder_button.clicked.connect(self.create_folder)

        # Add the checkbox and button to the horizontal layout
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.toggle_duplicates)
        h_layout.addWidget(self.create_folder_button)

        # Add the horizontal layout to the main layout
        layout.addLayout(h_layout)

        # Create a table view for search results
        self.search_results = QTableWidget(0, 7)
        self.search_results.setHorizontalHeaderLabels(["Name", "Extension", "Size (KB/MB)", "Location", "Creation Date", "Modification Date", "Checksum"])
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

        # Calculate checksums for all files in the selected directory
        checksums = {}
        for file_name in os.listdir(self.directory):
            file_path = os.path.join(self.directory, file_name)
            if os.path.isfile(file_path):  # Check if the path is a file
                with open(file_path, 'rb') as f:
                    data = f.read()
                    checksum = hashlib.md5(data).hexdigest()
                    checksums[file_path] = checksum

        # Find duplicate files
        duplicates = {}
        for file_path, checksum in checksums.items():
            if checksum not in duplicates:
                duplicates[checksum] = []
            duplicates[checksum].append(file_path)

        # Display files in the table
        if self.toggle_duplicates.isChecked():  # If the checkbox is checked
            for file_paths in duplicates.values():
                if len(file_paths) > 1:  # This is a set of duplicate files
                    for file_path in file_paths:
                        self.add_file_to_table(file_path, checksums[file_path], QColor('red'))
        else:  # If the checkbox is not checked
            for file_path in checksums.keys():  # This includes all files
                self.add_file_to_table(file_path, checksums[file_path])

        # Always display directories in the table
        for file_name in os.listdir(self.directory):
            file_path = os.path.join(self.directory, file_name)
            if os.path.isdir(file_path):  # If the path is a directory
                self.add_directory_to_table(file_path)
        # Display directories in the table if the checkbox is not checked
        # if not self.toggle_duplicates.isChecked():
        #     for file_name in os.listdir(self.directory):
        #         file_path = os.path.join(self.directory, file_name)
        #         if os.path.isdir(file_path):  # If the path is a directory
        #             self.add_directory_to_table(file_path)

        self.file_count_label.setText(f"Total Files: {self.search_results.rowCount()}")

    def add_file_to_table(self, file_path, checksum, color=None):
        # Add the file to the table
        row = self.search_results.rowCount()
        self.search_results.insertRow(row)
        self.search_results.setItem(row, 0, QTableWidgetItem(os.path.basename(file_path)))
        self.search_results.setItem(row, 1, QTableWidgetItem(os.path.splitext(file_path)[1]))
        file_size = os.path.getsize(file_path) / 1024  # Size in KB
        if file_size > 1024:  # If size > 1024 KB, convert it to MB
            file_size = file_size / 1024
            self.search_results.setItem(row, 2, QTableWidgetItem(f"{file_size:.2f} MB"))
        else:
            self.search_results.setItem(row, 2, QTableWidgetItem(f"{file_size:.2f} KB"))
        self.search_results.setItem(row, 3, QTableWidgetItem(file_path))
        creation_date = datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        self.search_results.setItem(row, 4, QTableWidgetItem(creation_date))
        modification_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        self.search_results.setItem(row, 5, QTableWidgetItem(modification_date))
        self.search_results.setItem(row, 6, QTableWidgetItem(checksum))

        # Color-code the row
        if color is not None:
            for i in range(7):
                self.search_results.item(row, i).setBackground(color)

    def add_directory_to_table(self, file_path):
        # Add the directory to the table
        row = self.search_results.rowCount()
        self.search_results.insertRow(row)
        self.search_results.setItem(row, 0, QTableWidgetItem(os.path.basename(file_path)))
        self.search_results.setItem(row, 1, QTableWidgetItem("<DIR>"))
        self.search_results.setItem(row, 2, QTableWidgetItem(""))
        self.search_results.setItem(row, 3, QTableWidgetItem(file_path))
        creation_date = datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        self.search_results.setItem(row, 4, QTableWidgetItem(creation_date))
        modification_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        self.search_results.setItem(row, 5, QTableWidgetItem(modification_date))
        self.search_results.setItem(row, 6, QTableWidgetItem(""))

    def contextMenuEvent(self, event):
        # Create a context menu
        context_menu = QMenu(self)

        # Add actions to the context menu
        # compare_action = QAction("Compare Files", self)
        # view_details_action = QAction("View Details", self)
        rename_action = QAction("Rename File", self)
        move_action = QAction("Move Duplicate File", self)
        delete_action = QAction("Delete Duplicate File", self)
        # context_menu.addAction(compare_action)
        # context_menu.addAction(view_details_action)
        context_menu.addAction(rename_action)
        context_menu.addAction(move_action)
        context_menu.addAction(delete_action)

        # Connect the actions to methods
        # compare_action.triggered.connect(self.compare_files)
        # view_details_action.triggered.connect(self.view_details)
        rename_action.triggered.connect(self.rename_file)
        move_action.triggered.connect(self.move_file)
        delete_action.triggered.connect(self.delete_file)

        # Show the context menu
        context_menu.exec_(self.mapToGlobal(event.pos()))

    def compare_files(self):
        # Implement file comparison here
        pass

    def view_details(self):
        # Implement view details here
        pass

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

        # Calculate checksums for all files in the selected directory
        checksums = {}
        for file_name in os.listdir(self.directory):
            file_path = os.path.join(self.directory, file_name)
            if os.path.isfile(file_path):  # Check if the path is a file
                with open(file_path, 'rb') as f:
                    data = f.read()
                    checksum = hashlib.md5(data).hexdigest()
                    checksums[file_path] = checksum

        # Find duplicate files
        duplicates = {}
        for file_path, checksum in checksums.items():
            if checksum not in duplicates:
                duplicates[checksum] = []
            duplicates[checksum].append(file_path)

        # Iterate over all files in the selected directory
        for file_name in os.listdir(self.directory):
            file_path = os.path.join(self.directory, file_name)
            if os.path.isfile(file_path):  # Check if the path is a file
                # Get the file's creation and modification dates
                creation_date = os.path.getctime(file_path)
                modification_date = os.path.getmtime(file_path)

                # Check if the search term is in the file name, the file has the selected extension, and the creation and modification dates are within the selected range
                if (search_term in file_name.lower() and (
                        selected_extension == "All Files" or os.path.splitext(file_name)[1] == selected_extension) and
                        start_date <= creation_date <= end_date and start_date <= modification_date <= end_date):
                    # Add the file to the search results
                    if self.toggle_duplicates.isChecked():  # If the checkbox is checked
                        if len(duplicates[file_path]) > 1:  # This is a set of duplicate files
                            self.add_file_to_table(file_path, checksums[file_path], QColor('red'))
                    else:  # If the checkbox is not checked
                        self.add_file_to_table(file_path, checksums[file_path])

        # Always display directories in the table
        for file_name in os.listdir(self.directory):
            file_path = os.path.join(self.directory, file_name)
            if os.path.isdir(file_path):  # If the path is a directory
                self.add_directory_to_table(file_path)

        self.file_count_label.setText(f"Loaded Files: {self.search_results.rowCount()}")

    # def file_search(self):
    #     # Get the search term from the search bar
    #     search_term = self.search_bar.text().lower()
    #
    #     # Get the selected extension from the dropdown
    #     selected_extension = self.extension_dropdown.currentText()
    #
    #     # Get the selected date range from the date edits
    #     start_date = self.start_date_edit.dateTime().toPyDateTime().timestamp()
    #     end_date = self.end_date_edit.dateTime().toPyDateTime().timestamp()
    #
    #     # Clear the table
    #     self.search_results.setRowCount(0)
    #
    #     # Iterate over all files in the selected directory
    #     for file_name in os.listdir(self.directory):
    #         # Get the file's creation and modification dates
    #         creation_date = os.path.getctime(os.path.join(self.directory, file_name))
    #         modification_date = os.path.getmtime(os.path.join(self.directory, file_name))
    #
    #         # Check if the search term is in the file name, the file has the selected extension, and the creation and modification dates are within the selected range
    #         if (search_term in file_name.lower() and (selected_extension == "All Files" or os.path.splitext(file_name)[1] == selected_extension) and
    #                 start_date <= creation_date <= end_date and start_date <= modification_date <= end_date):
    #             # Get the file size
    #             file_size = os.path.getsize(os.path.join(self.directory, file_name)) / 1024  # Size in KB
    #             if file_size > 1024:  # If size > 1024 KB, convert it to MB
    #                 file_size = file_size / 1024
    #                 size_str = f"{file_size:.2f} MB"
    #             else:
    #                 size_str = f"{file_size:.2f} KB"
    #
    #             # Add the file to the search results
    #             row = self.search_results.rowCount()
    #             self.search_results.insertRow(row)
    #             self.search_results.setItem(row, 0, QTableWidgetItem(file_name))
    #             self.search_results.setItem(row, 1, QTableWidgetItem(os.path.splitext(file_name)[1]))
    #             self.search_results.setItem(row, 2, QTableWidgetItem(size_str))
    #             self.search_results.setItem(row, 3, QTableWidgetItem(os.path.join(self.directory, file_name)))
    #             self.search_results.setItem(row, 4, QTableWidgetItem(
    #                 datetime.fromtimestamp(creation_date).strftime('%Y-%m-%d %H:%M:%S')))
    #             self.search_results.setItem(row, 5, QTableWidgetItem(
    #                 datetime.fromtimestamp(modification_date).strftime('%Y-%m-%d %H:%M:%S')))
    #
    #     self.file_count_label.setText(f"Loaded Files: {self.search_results.rowCount()}")

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

    def rename_file(self):
        # Get the selected file
        selected_items = self.search_results.selectedItems()
        if selected_items:
            # Get the file path from the first selected item's row
            file_path = self.search_results.item(selected_items[0].row(), 3).text()

            # Ask the user for a new name
            new_name, ok = QInputDialog.getText(self, "Rename File", "Enter new name:")

            if ok and new_name:  # If the user entered a new name
                # Get the file extension
                _, extension = os.path.splitext(file_path)

                # Rename the file
                new_file_path = os.path.join(os.path.dirname(file_path), new_name + extension)
                os.rename(file_path, new_file_path)

                # Update the file path in the table
                self.search_results.setItem(selected_items[0].row(), 3, QTableWidgetItem(new_file_path))

                # Display all files in the selected directory
                self.display_files()

    def move_file(self):
        # Get the selected file
        selected_items = self.search_results.selectedItems()
        if selected_items:
            # Get the file path from the first selected item's row
            file_path = self.search_results.item(selected_items[0].row(), 3).text()

            # Ask the user for a destination directory
            destination_directory = QFileDialog.getExistingDirectory(self, "Select Directory")

            if destination_directory:  # If the user selected a directory
                # Move the file
                new_file_path = os.path.join(destination_directory, os.path.basename(file_path))
                shutil.move(file_path, new_file_path)

                # Remove the file from the table
                self.search_results.removeRow(selected_items[0].row())

                # Refresh the file list
                self.display_files()

    def delete_file(self):
        # Get the selected file
        selected_items = self.search_results.selectedItems()
        if selected_items:
            # Get the file path from the first selected item's row
            file_path = self.search_results.item(selected_items[0].row(), 3).text()

            # Ask the user for confirmation
            reply = QMessageBox.question(self, 'Delete File', "Are you sure you want to delete this file?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:  # If the user confirmed the deletion
                # Delete the file
                os.remove(file_path)

                # Remove the file from the table
                self.search_results.removeRow(selected_items[0].row())

                # Refresh the file list
                self.display_files()

    def create_folder(self):
        # Ask the user for the new folder's name
        folder_name, ok = QInputDialog.getText(self, "Create Folder", "Enter folder name:")

        if ok and folder_name:  # If the user entered a folder name
            # Create the new folder
            os.makedirs(os.path.join(self.directory, folder_name), exist_ok=True)

            # Refresh the file list
            self.display_files()

def main():
    app = QApplication(sys.argv)
    # Apply QDarkStyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    mainWin = FileCompanion()
    mainWin.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
