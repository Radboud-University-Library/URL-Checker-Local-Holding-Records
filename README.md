# URL Checker for Local Holding Records

## Overview

The URL Checker is a GUI application for checking the HTTP response of URLs from a CSV file. The application allows users to:

## Features

- Select input and output location using a file dialog.
- Read URLs from a CSV file. The CSV file should have a column named `LHR Electronic Location URI`.
- Check HTTP response codes for URLs.
- Handle URL redirections.
- Display processing status and progress in the GUI.
- Save the processed results to a CSV file.

## Requirements

- Python 3.11
- pandas
- requests==2.31.0

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Feelingthefoo/link-checker-app-lhr.git
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the application:
    ```sh
    python main.py
    ```

## Creating an Executable

You can create an executable for the application using PyInstaller:

1. Install PyInstaller:
    ```sh
    pip install pyinstaller
    ```

2. Create the executable:
    ```sh
    pyinstaller --onefile --windowed main.py
    ```

3. The executable will be created in the `dist` directory.
    
## File Structure

- `main.py`: The main GUI application file.
- `link_functions.py`: Contains functionalities for checking HTTP responses of URLs and utility functions for file selection.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.