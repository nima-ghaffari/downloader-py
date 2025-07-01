# Advanced Download Manager

This project presents an "Advanced Download Manager," a robust and user-friendly application crafted to streamline your file downloading processes. Developed in Python, it utilizes the `tkinter` library for its intuitive graphical interface and the `requests` library for reliable HTTP interactions. The core philosophy behind this manager is to combine powerful functionality with a polished and modern user experience.

## Core Capabilities

The Advanced Download Manager is equipped with a suite of features designed to make your downloading experience seamless and efficient:

- **Multi-threaded Download Execution:** The application is engineered to perform downloads concurrently using a thread pool. This means multiple files can be downloaded simultaneously in the background, ensuring the user interface remains responsive and improving overall download efficiency.
- **Flexible Filename Customization:**
  - **Batch Naming:** For scenarios involving multiple files, you can define a single base filename (e.g., "Lecture_Series"), and the manager will automatically append sequential numbers (e.g., `Lecture_Series_001.mp4`, `Lecture_Series_002.mp4`), promoting excellent organization.
  - **Individual Naming:** Should you require unique identifiers for specific files, the application allows for custom filename assignment for each URL, providing granular control.
  - **Intelligent Extension Detection:** A built-in mechanism intelligently attempts to determine the correct file extension (such as `.mp4`, `.srt`, `.pdf`, `.zip`) by analyzing the URL's path and, if necessary, by inspecting HTTP `Content-Type` headers. This significantly reduces the occurrence of generic or incorrect file extensions like `.bin`.
- **Comprehensive Download Control:**
  - **Start, Pause, and Resume:** Users have full control to initiate, temporarily halt, or continue ongoing downloads.
  - **Stop All:** A dedicated function to immediately cease all active downloads and clear any pending items from the download queue.
  - **"Another" Functionality:** This unique feature acts as a complete reset button, purging all current download data (active, queued, completed, and failed lists) and resetting internal configurations, preparing the application for an entirely new set of downloads.
- **Dynamic Progress Visualization:**
  - The user interface provides real-time updates on download status. For files with a discernible total size, it displays precise percentage completion and live download speed.
  - Crucially, for files where the total size is unknown (e.g., certain streaming content), the progress indicator shows "N/A" for percentage, but continuously updates the accumulated downloaded size (e.g., `5.2 MB / Unknown`) along with the live download speed, ensuring constant feedback.
  - Clear status messages (e.g., "Downloading," "Paused," "Completed," "Error") keep you informed about each file's state.
- **Modern and Intuitive User Interface (UI):**
  - The application boasts a clean, minimalist design with a carefully chosen dark blue and vibrant accent color scheme, derived from Oklch values, aiming for a sophisticated visual appeal.
  - All buttons are uniformly styled with consistent sizing, a distinct bold font (Berlin Sans Demi, with a robust fallback), and clear white text, ensuring a cohesive look.
  - Custom-designed scrollbars enhance the visual aesthetic while maintaining smooth functionality.
  - Optimized spacing throughout the interface prevents clutter and promotes readability, contributing to an overall pleasant user experience.
- **Intelligent Exit Mechanism:**
  - The "Exit" button located at the bottom-right features dynamic visual feedback. It turns **red** on hover if any downloads are actively running, and **yellow** if there are files pending in the queue, serving as a subtle warning.
  - Upon clicking, the system intelligently prompts for confirmation, adapting its message based on the presence of active downloads or pending queues, thus ensuring data integrity before gracefully terminating the application.

## Getting Started

### Prerequisites

- Python 3.x installed on your operating system.

### How to Run

1.  **Acquire the Script:** Ensure you have the `main_downloader.py` script saved on your computer.
2.  **Execute the Application:** Open your terminal or command prompt, navigate to the directory where `main_downloader.py` is located, and execute the following command:
    ```bash
    python main_downloader.py
    ```

## Usage Guide

1.  **Define Your Save Path:**
    - Locate the "Save to:" field.
    - Click the "Browse" button next to it to select the desired directory where your downloaded files will be stored.
2.  **Input Download URLs:**
    - Paste your download links into the "Enter URLs (one per line):" text area. Each URL should be on a separate line.
    - Click the "Add URLs" button to populate your download list.
3.  **Customize Filenames (Optional):**
    - **Set Names:** Click "Set Names" to open a dialogue box. You can opt for "Batch Naming" (where files are automatically numbered sequentially from a base name) or "Individual Names" (allowing you to manually assign a unique name for each file).
    - **Reset Names:** To revert all custom or batch filenames to their default, URL-derived names, click "Reset Names."
4.  **Monitor Your Downloads (Downloads Section):**
    - This section displays the status of all your added URLs in a table format.
    - **Filename:** The name of the file being downloaded.
    - **Size:** The total size of the file (or current downloaded amount if total is unknown).
    - **Progress / Speed:** The percentage of download completion (or "N/A" if total size is unknown) and the live download speed.
    - **Status:** The current state of the download (e.g., "Ready", "Downloading", "Paused", "Completed", "Error").
5.  **Control Your Downloads:**
    - **Start All:** Initiates the download process for all items in the queue.
    - **Pause / Resume:** Toggles the state of currently active downloads between paused and resumed.
    - **Stop All:** Commands all active downloads to cease immediately and clears any pending items from the queue.
    - **Another:** Clears the entire download session, including active, queued, completed, and failed items, preparing the manager for a fresh start.
6.  **Exiting the Application:**
    - Locate the "Exit" button in the bottom-right corner.
    - Observe its dynamic visual feedback on hover.
    - Upon clicking, the system will provide tailored prompts to ensure a smooth exit, especially if downloads are in progress or pending.

## Implementation Insights

This section provides a brief overview of key technical aspects contributing to the manager's functionality and user experience:

- **Concurrency:** Multi-threading is implemented using Python's `concurrent.futures.ThreadPoolExecutor`, allowing for efficient background processing of downloads without freezing the user interface.
- **Dynamic UI Styling:** The modern aesthetic and consistent theme are primarily achieved through `tkinter.ttk.Style`. Custom styles are defined to apply specific colors, fonts, and visual properties to various `ttk` widgets.
- **Responsive Progress Tracking:** The `download_file` method dynamically updates `downloaded_bytes` during stream processing. This allows the UI to display the amount downloaded even when the `Content-Length` HTTP header (total size) is unavailable. For completed downloads, `total_size` is accurately set to the final `downloaded_bytes` if it was initially unknown, ensuring correct reporting.
- **Advanced Exit Button:** The nuanced behavior of the "Exit" button, including its dynamic color changes on hover and intelligent confirmation prompts, is managed by utilizing a standard `tk.Button`. This choice allows for direct control over its `background` and `activebackground` properties via event bindings (`<Enter>`, `<Leave>`, `<Button-1>`), which `ttk.Button` does not natively expose for such custom application-state-driven styling.

---

**Created by Nima-Ghaffari**

[![portfolio](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/nimaghaffari001)

---
