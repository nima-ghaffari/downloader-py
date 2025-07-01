# Advanced Download Manager

This project introduces an Advanced Download Manager, a robust application designed to streamline your file downloading experience. Developed using Python's `tkinter` for the graphical user interface and `requests` for handling robust HTTP operations, this manager aims to offer both functionality and a pleasant user experience.

## Core Capabilities

* **Multi-threaded Efficiency:** The application leverages multi-threading to facilitate concurrent downloads, significantly enhancing download speed and efficiency.
* **Flexible Filename Management:**
    * **Batch Naming:** Users can define a base name, and the system will automatically append sequential numbering (e.g., `My_Project_001.zip`, `My_Project_002.zip`), ensuring organized file management.
    * **Individual Naming:** The option to assign unique, custom filenames for each URL provides granular control over downloaded content.
    * **Intelligent Extension Detection:** The manager intelligently attempts to determine the correct file extension (e.g., `.mp4`, `.srt`, `.pdf`) by analyzing URL patterns and HTTP content-type headers, minimizing the occurrence of generic `.bin` extensions.
* **Comprehensive Download Controls:**
    * Initiate, pause, and resume ongoing downloads with ease.
    * A "Stop All" function allows for the immediate cessation of all active and queued downloads.
    * The "Another" feature provides a clean slate, clearing all current download information and resetting the application for new tasks.
* **Dynamic Progress Visualization:**
    * The user interface provides real-time updates on download progress, including percentage completion and live download speed for files where the total size is known.
    * For files with indeterminate total sizes (e.g., streaming content), the system dynamically displays `N/A` for percentage, alongside the accumulated downloaded amount and live speed, offering continuous feedback.
    * Clear status indicators (Downloading, Paused, Completed, Error) ensure users are always informed.
* **Modern and Intuitive User Interface:**
    * The application boasts a clean, minimalist design complemented by a sophisticated dark blue and vibrant accent color scheme, meticulously crafted from Oklch values.
    * Buttons are consistently styled with a uniform size and utilize the "Berlin Sans Demi" font (with a suitable fallback) and crisp white text.
    * Custom-designed scrollbars enhance visual appeal while maintaining functionality.
    * Optimized spacing contributes to a clutter-free and user-friendly layout.
* **Intelligent Exit Mechanism:**
    * The dedicated "Exit" button features dynamic visual cues: it glows **red** upon hover if downloads are active, and **yellow** if downloads are merely queued, signaling the potential impact of exiting.
    * When clicked, the application intelligently prompts the user for confirmation, offering tailored options to stop ongoing downloads or clear pending queues before gracefully terminating.

## Getting Started

### Prerequisites

* Python 3.x installed on your system.
* The `requests` library for handling HTTP requests.

### Installation Steps

1.  **Install `requests`:**
    Open your terminal or command prompt and execute the following command:
    ```bash
    pip install requests
    ```
2.  **Acquire the Script:**
    Save the provided Python code into a file named `main_downloader.py` (or any other name ending with `.py`).

### How to Run

Navigate to the directory containing `main_downloader.py` in your terminal or command prompt, and run:

```bash
python main_downloader.py