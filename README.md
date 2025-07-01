# Advanced Download Manager

This is a multi-threaded download manager application built using Python's `tkinter` for the graphical user interface and `requests` for handling downloads. It features a modern, minimalist design with a customizable color theme and advanced download controls.

## Features

-   **Multi-threaded Downloads:** Efficiently download multiple files concurrently.
-   **Customizable Filenames:**
    -   **Batch Naming:** Set a base name for all files, and the application will automatically append sequential numbers (e.g., `My_File_001.ext`).
    -   **Individual Naming:** Manually set a unique filename for each URL.
    -   **Smart Extension Detection:** Automatically suggests file extensions (like `.mp4`, `.srt`, `.pdf`) based on URL patterns and content type headers.
-   **Download Controls:**
    -   Start, Pause, and Resume downloads.
    -   Stop all active and queued downloads.
    -   Clear all content to prepare for new downloads.
-   **Dynamic Progress Display:**
    -   Shows download progress percentage and real-time speed for files with known total sizes.
    -   For files with unknown total sizes, it displays `N/A` for percentage, the current downloaded amount, and the live download speed.
    -   Updates status (Downloading, Paused, Completed, Error).
-   **Modern User Interface (UI):**
    -   Clean, minimalist design with a dark blue and vibrant accent color scheme (based on Oklch values).
    -   Consistently styled buttons with "Berlin Sans Demi" (or a fallback) font and white text.
    -   Sleek custom scrollbars.
    -   Compact spacing for efficient use of screen space.
-   **Intuitive Exit Behavior:**
    -   An "Exit" button with dynamic hover effects: turns **red** if downloads are active, and **yellow** if downloads are queued.
    -   Clicking the "Exit" button prompts for confirmation based on download status (active downloads or pending queue) before stopping and exiting.

## Color Palette Used (Oklch to Hex)

The UI adheres strictly to the following Oklch-derived color palette:

-   **Main Text Color:** `oklch(0.97 0.014 254.604)` -> `#F7F8FF` (Very light blue-white)
-   **Main Background & Borders:** `oklch(0.208 0.042 265.755)` -> `#162B4A` (Deep dark blue)
-   **Accent & Button Background:** `oklch(0.424 0.199 265.638)` -> `#006EE5` (Vibrant medium blue)
-   **Input Fields & Table Background:** `#D7E5FF` (A very light blue for readability)

## Installation

1.  **Prerequisites:**
    -   Python 3.x installed on your system.
    -   `requests` library for HTTP requests.

2.  **Install `requests`:**
    Open your terminal or command prompt and run:
    ```bash
    pip install requests
    ```

3.  **Download the script:**
    Save the provided Python code into a file named `main_downloader.py` (or any other `.py` extension).

## Usage

1.  **Run the application:**
    Open your terminal or command prompt, navigate to the directory where you saved `main_downloader.py`, and run:
    ```bash
    python main_downloader.py
    ```

2.  **Set Save Path:**
    -   Click the "Browse" button next to the "Save to:" field to choose the directory where downloaded files will be saved.

3.  **Add URLs:**
    -   Paste one or more download links into the "Enter URLs (one per line):" text area.
    -   Click "Add URLs" to add them to the download list.

4.  **Manage Filenames (Optional):**
    -   **Set Names:** Click "Set Names" to choose between "Batch Naming" (e.g., `My_Video_001.mp4`, `My_Video_002.mp4`) or "Individual Names" (manually assign each filename).
    -   **Reset Names:** Click "Reset Names" to revert all custom/batch filenames to their default (derived from the URL).

5.  **Control Downloads:**
    -   **Start All:** Begins downloading all URLs in the list.
    -   **Pause / Resume:** Toggles between pausing and resuming active downloads.
    -   **Stop All:** Stops all active downloads and clears the queue.
    -   **Another:** Clears all current download information (active, queued, completed, failed) and resets the application, preparing it for a new set of downloads.

6.  **Exit the Application:**
    -   Click the "Exit" button in the bottom right corner.
    -   The button's color will dynamically change on hover (red for active downloads, yellow for queued downloads) to indicate urgency.
    -   Depending on the download status, it will prompt for confirmation before stopping downloads (if any) and exiting.

## Author

-   Created by Nima-Ghaffari