# File Companion

File Companion is a user-friendly desktop application that allows users to manage their files and folders efficiently. It’s built with PyQt5 and styled with QDarkStyle.

## Features

- Powerful file search engine with filters for name, extension, size, creation/modification dates.
- User-friendly interface with modern design.
- Added a dedicated panel for file search with a search bar and list view for search results.
- The search results are displayed in a table with each item containing file details like name, extension, size, location, creation date, and modification date.
- Added options to select file directory manually with default as the current directory.
- Double-clicking a file in the search results opens the file with the default application for that file type.
- **New in 1.2.0.0**: Added support for identifying and highlighting duplicate files in the selected directory.
- **New in 1.3.0.0**: Added options to move or delete duplicate files directly from the search results table. Also added an option to create new folders directly from the application.

## How to Use

1. Click the ‘Select Directory’ button to select a directory for file management.
2. Use the search bar to enter search terms. The application will list all files in the selected directory that match the search term.
3. The search results are displayed in a table. Each row in the table represents a file and contains details like name, extension, size, location, creation date, and modification date.
4. Double-click a file in the search results to open the file with the default application for that file type.
5. Check the 'Show only duplicates' box to highlight duplicate files in the search results.
6. Right-click a file in the search results to move or delete the file.
7. Click the 'Create Folder' button to create a new folder in the selected directory.

## Built With

- Python
- PyQt5
- QDarkStyle
