"""
link_functions.py: Contains functionalities for checking HTTP responses of URLs and utility functions for file selection.

Classes:
- LinkProcessor: Encapsulates methods for processing URLs and interacting with the file system.
"""

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor


class LinkProcessor:

    def __init__(self):
        pass

    @staticmethod
    def get_http_response_code(url, retries=3, backoff_factor=0.3, timeout=5, allow_redirects=True):
        """
        Get HTTP response code for a given URL.

        Args:
        - url (str): The URL to check.
        - retries (int): Number of retry attempts.
        - backoff_factor (float): A backoff factor to apply between attempts.
        - timeout (int or float): How many seconds to wait for the server to send data
          before giving up.

        Returns:
        - int or str: HTTP response code or "Error" if there was a problem.
        """
        session = requests.Session()

        retry = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
            allowed_methods=["HEAD", "GET", "OPTIONS"]  # Retry only on these HTTP methods
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        try:
            response = session.get(url, timeout=timeout, allow_redirects=allow_redirects, stream=True)
            redirected_url = None
            if 300 <= response.status_code < 400:
                redirected_url = response.headers.get('Location')

            return response.status_code, redirected_url
        except requests.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                return e.response.status_code, None
            else:
                return "Error", None

    @staticmethod
    def http_code_description(code):
        """
        Return a brief description based on the HTTP response code.

        Args:
        - code (int or str): The HTTP response code.

        Returns:
        - str: A brief description of the response code.
        """
        if code in (100, 101, 102, 103):
            return "Informational Response"
        elif code in (200, 201, 202, 203, 204, 205, 206, 207, 208, 226):
            return "Successful"
        elif code in (300, 301, 302, 303, 304, 305, 306, 307, 308):
            return "Redirection"
        elif code in (400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 421, 422, 423, 424, 425, 426, 427, 428, 429, 431, 451):
            return "Client Errors"
        elif code in (500, 501, 502, 503, 504, 505, 506, 507, 508, 510, 511):
            return "Server Errors"
        else:
            return "Unknown"

    def process_links(self, input_path, output_path, status_text, progress_bar=None, root=None, allow_redirects=True):

        """
        Process the input CSV file, check each URL's HTTP response, and save the results to the output file.

        Args:
        - input_path (str): Path to the input CSV file.
        - output_path (str): Path to save the processed CSV file.
        - status_text (tkinter.Text): Text widget to update the processing status.
        - progress_bar (tkinter.ttk.Progressbar, optional): Progress bar widget to show the processing progress.
        - root (tkinter.Tk, optional): Main GUI root.
        """
        def update_status(message):
            status_text.delete(1.0, 'end')
            status_text.insert('end', message)

        def update_progress(value):
            progress_bar["value"] = value
            percentage = round(progress_bar["value"] / progress_bar["maximum"] * 100)
            update_status(f"Processing... {percentage}%\n")

        root.after(0, update_status, "Reading the CSV file...\n")

        try:
            df = pd.read_csv(input_path, header=0, delimiter=';')
            df['LHR Electronic Location URI'] = df['LHR Electronic Location URI'].str.split('|')
            df = df.explode('LHR Electronic Location URI')

            if progress_bar:
                progress_bar["maximum"] = len(df)
                progress_bar["value"] = 0

            def process_url(url):
                code, redirected_url = self.get_http_response_code(url, allow_redirects=allow_redirects)
                if progress_bar:
                    root.after(0, update_progress, progress_bar["value"] + 1)
                return code, redirected_url

            with ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(process_url, df['LHR Electronic Location URI']))
                df['HTTPResponseCode'] = [result[0] for result in results]
                df['RedirectedURL'] = [result[1] for result in results]

            df['HTTPResponseDescription'] = df['HTTPResponseCode'].apply(self.http_code_description)

            # After processing all URLs and adding new columns:
            original_columns = [col for col in df.columns if
                                col not in ['HTTPResponseCode', 'HTTPResponseDescription', 'RedirectedURL']]
            new_column_order = original_columns + ['HTTPResponseCode', 'HTTPResponseDescription', 'RedirectedURL']

            # Reorder the DataFrame columns:
            df = df[new_column_order]

            # Save the reordered DataFrame to the CSV file:
            df.to_csv(output_path, index=False)

            if progress_bar:
                progress_bar["value"] = progress_bar["maximum"]
            root.after(0, update_status, "Processing completed. File saved.\n")

        except pd.errors.ParserError as e:
            error_message = str(e)
            root.after(0, update_status, f"Error processing the file: {error_message}\n")
        except ValueError as e:
            error_message = str(e)
            root.after(0, update_status, f"Error: {error_message}\n")

    @staticmethod
    def select_input_file():
        """Open a file dialog to select a CSV input file.

        Returns:
        - str: Path to the selected file.
        """
        return filedialog.askopenfilename(title="Select a CSV file", filetypes=[("CSV files", "*.csv")])

    @staticmethod
    def select_output_location():
        """Open a file dialog to select an output location for the processed CSV file.

        Returns:
        - str: Path to the selected location.
        """
        return filedialog.asksaveasfilename(title="Select Save Location", defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")])
