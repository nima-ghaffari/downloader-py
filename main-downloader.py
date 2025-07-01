import os
import requests
import time
import math
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, unquote
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from threading import Thread
from queue import Queue
from tkinter.font import Font
import subprocess

class CustomTheme:
    """Applies a custom visual theme to Tkinter widgets."""
    @staticmethod
    def apply(root, fonts):
        # Define color palette
        text_color = '#F7F8FF'
        bg_color = '#162B4A'
        accent_color = '#006EE5'

        entry_field_bg = '#D7E5FF'
        entry_text_color = bg_color
        
        button_text_color = '#FFFFFF' 
        
        border_color = bg_color
        
        selected_item_bg = accent_color
        selected_item_text = text_color
        
        disabled_color_bg = '#4A6278'
        disabled_color_fg = '#BDC3C7'
        hover_color = '#004CAF'

        # Apply ttk.Style
        style = ttk.Style()
        
        # Try to use 'clam' theme, fallback to 'default'
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        else:
            style.theme_use('default')

        # Configure default font for all ttk widgets
        style.configure('.', font=fonts['default'])  

        # Configure root window background
        root.configure(bg=bg_color)

        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=text_color)
        
        # Configure TCheckbutton
        style.configure('TCheckbutton', 
                        font=fonts['default'], 
                        background=bg_color, 
                        foreground=text_color, 
                        indicatoron=True, 
                        padding=3)
        style.map('TCheckbutton',
                  background=[('active', bg_color)], 
                  foreground=[('disabled', disabled_color_fg)])
        
        # Configure TEntry for error/success states
        style.configure('TEntry.Error', fieldbackground='#FF6347', foreground='white')  
        style.configure('TEntry.Success', fieldbackground='#8BC34A', foreground='white')  
        
        # Configure TLabelFrame (for grouping widgets)
        style.configure('TLabelFrame', 
                        background=accent_color, 
                        foreground=text_color,  
                        bordercolor=border_color, 
                        relief='solid',    
                        borderwidth=1,
                        font=fonts['heading'])  
        style.map('TLabelFrame', background=[('active', accent_color)])  
        
        # Configure TButton
        style.configure('TButton', 
                        background=accent_color,
                        foreground=button_text_color, 
                        padding=[10, 5],   
                        relief='flat',     
                        bordercolor=accent_color,   
                        focusthickness=0,
                        font=fonts['button'])   
        style.map('TButton',
                  background=[('active', hover_color), ('disabled', disabled_color_bg)],   
                  foreground=[('disabled', disabled_color_fg)])   

        # Configure TEntry
        style.configure('TEntry',
                        fieldbackground=entry_field_bg,   
                        foreground=entry_text_color,     
                        insertbackground=entry_text_color,   
                        selectbackground=selected_item_bg,   
                        selectforeground=selected_item_text,   
                        bordercolor=border_color,   
                        relief='solid',
                        borderwidth=1,   
                        padding=5)
        
        # Configure ScrolledText (tk widget, so options are set directly on root)
        root.option_add('*Scrolledtext*background', entry_field_bg)
        root.option_add('*Scrolledtext*foreground', entry_text_color)
        root.option_add('*Scrolledtext*insertBackground', entry_text_color)
        root.option_add('*Scrolledtext*selectBackground', selected_item_bg)
        root.option_add('*Scrolledtext*selectForeground', selected_item_text)
        root.option_add('*Scrolledtext*borderwidth', 1)
        root.option_add('*Scrolledtext*relief', 'solid')
        root.option_add('*Scrolledtext*highlightbackground', border_color)   
        root.option_add('*Scrolledtext*highlightcolor', accent_color)   

        # Configure Treeview
        style.configure('Treeview',
                        background=entry_field_bg,   
                        foreground=entry_text_color,   
                        fieldbackground=entry_field_bg,
                        bordercolor=border_color,   
                        relief='solid',    
                        borderwidth=1,
                        padding=3)
        style.map('Treeview',
                  background=[('selected', selected_item_bg)],   
                  foreground=[('selected', selected_item_text)])   

        # Configure Treeview Heading
        style.configure('Treeview.Heading',
                        background=accent_color,   
                        foreground=text_color,     
                        relief='flat',
                        padding=5,
                        font=fonts['heading'])   
        style.map('Treeview.Heading',
                  background=[('active', hover_color)])   

        # Configure Status Label
        style.configure('TStatus.TLabel',   
                        background=bg_color,   
                        foreground=text_color,   
                        relief='sunken',   
                        padding=[5,2],   
                        anchor='w')   

        # Configure Downloads Heading Label
        style.configure('DownloadsHeading.TLabel',
                        background=bg_color,   
                        foreground=text_color,   
                        font=fonts['heading'],   
                        padding=(0, 5, 0, 2))   

        # Configure Scrollbar
        style.configure("TScrollbar",
                        troughcolor=bg_color,   
                        background=accent_color,   
                        bordercolor=bg_color,   
                        arrowcolor=text_color,   
                        relief='flat',   
                        borderwidth=0)   

        style.map("TScrollbar",
                  background=[('active', hover_color), ('!disabled', accent_color)],
                  troughcolor=[('active', bg_color)],
                  arrowcolor=[('active', 'white')])

        # Apply styles to Toplevel, Dialog, Message for consistency
        root.option_add('*Toplevel*background', bg_color)   
        root.option_add('*Dialog*background', bg_color)
        root.option_add('*Dialog*foreground', text_color)
        root.option_add('*Message*background', bg_color)
        root.option_add('*Message*foreground', text_color)
        root.option_add('*Button*background', accent_color)   
        root.option_add('*Button*foreground', button_text_color) 
        style.configure('Dialog.TButton', background=accent_color, foreground=button_text_color) 

class CustomFilenameDialog(tk.Toplevel):
    """A custom Tkinter Toplevel window for filename input with custom styling."""
    def __init__(self, parent, title, prompt_text, initial_value, fonts, colors):
        super().__init__(parent)
        self.transient(parent) # Set to be on top of parent
        self.grab_set() # Grab focus, preventing interaction with parent
        self.title(title)
        self.parent = parent
        self.result = None # Stores the user's input
        self.fonts = fonts
        self.colors = colors

        # Center the dialog on the parent window
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.configure(bg=self.colors['bg_color']) 

        self.create_widgets(prompt_text, initial_value)

        # Handle window close button gracefully
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.wait_window(self) # Wait until this window is closed

    def create_widgets(self, prompt_text, initial_value):
        # Prompt Label
        prompt_label = tk.Label(self, text=prompt_text, font=self.fonts['default'], 
                                 fg=self.colors['text_color'], bg=self.colors['bg_color'], pady=10)
        prompt_label.pack(padx=10, pady=5)

        # Entry for filename input
        self.entry_var = tk.StringVar(value=initial_value)
        self.entry = ttk.Entry(self, textvariable=self.entry_var, font=self.fonts['default'], width=50)
        self.entry.pack(padx=10, pady=5, fill=tk.X)
        self.entry.bind("<Return>", lambda event: self.ok()) # Bind Enter key to OK
        self.entry.focus_set() # Set focus to the entry widget

        # Buttons frame
        button_frame = ttk.Frame(self, style='TFrame')
        button_frame.pack(pady=10)

        ok_button = ttk.Button(button_frame, text="OK", command=self.ok, width=10)
        ok_button.pack(side=tk.LEFT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel, width=10)
        cancel_button.pack(side=tk.LEFT, padx=5)

    def ok(self):
        """Sets the result and destroys the dialog."""
        self.result = self.entry_var.get()
        self.destroy()

    def cancel(self):
        """Cancels the dialog, setting result to None."""
        self.result = None
        self.destroy()


class BatchDownloadDialog(tk.Toplevel):
    """A custom Tkinter Toplevel window for numbered batch download input."""
    def __init__(self, parent, fonts, colors):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Numbered Batch Download")
        self.parent = parent
        self.fonts = fonts
        self.colors = colors
        self.result = None # (template_url, start_num, end_num, num_digits_str)

        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        self.configure(bg=self.colors['bg_color'])

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.wait_window(self)

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='TFrame', padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Template URL
        ttk.Label(main_frame, text="Template URL (use # for numbers, e.g., http://site.com/image-#.jpg):", font=self.fonts['default']).pack(anchor=tk.W, pady=(0,2))
        self.template_url_var = tk.StringVar()
        self.template_entry = ttk.Entry(main_frame, textvariable=self.template_url_var, font=self.fonts['default'], width=60)
        self.template_entry.pack(fill=tk.X, pady=(0,10))
        self.template_entry.focus_set()

        # Start Number
        ttk.Label(main_frame, text="Start Number:", font=self.fonts['default']).pack(anchor=tk.W, pady=(0,2))
        self.start_num_var = tk.StringVar(value="1")
        self.start_num_entry = ttk.Entry(main_frame, textvariable=self.start_num_var, font=self.fonts['default'], width=10)
        self.start_num_entry.pack(anchor=tk.W, pady=(0,5))

        # End Number
        ttk.Label(main_frame, text="End Number:", font=self.fonts['default']).pack(anchor=tk.W, pady=(0,2))
        self.end_num_var = tk.StringVar(value="10")
        self.end_num_entry = ttk.Entry(main_frame, textvariable=self.end_num_var, font=self.fonts['default'], width=10)
        self.end_num_entry.pack(anchor=tk.W, pady=(0,10))

        # Number of Digits for Padding
        ttk.Label(main_frame, text="Number of Digits for Padding (e.g., 3 for '001', leave empty for no padding):", font=self.fonts['default']).pack(anchor=tk.W, pady=(0,2))
        self.num_digits_var = tk.StringVar(value="")
        self.num_digits_entry = ttk.Entry(main_frame, textvariable=self.num_digits_var, font=self.fonts['default'], width=10)
        self.num_digits_entry.pack(anchor=tk.W, pady=(0,10))
        ttk.Label(main_frame, text="Example: if URL is 'image-00#.jpg' and start number is 1, set digits to 3.", font=self.fonts['default'], foreground=self.colors['disabled_color_fg']).pack(anchor=tk.W)


        # Buttons
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(pady=10)

        ok_button = ttk.Button(button_frame, text="Generate & Add", command=self.ok, width=15)
        ok_button.pack(side=tk.LEFT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel, width=10)
        cancel_button.pack(side=tk.LEFT, padx=5)

    def ok(self):
        template_url = self.template_url_var.get().strip()
        start_num_str = self.start_num_var.get().strip()
        end_num_str = self.end_num_var.get().strip()
        num_digits_str = self.num_digits_var.get().strip()

        if not template_url or '#' not in template_url:
            messagebox.showwarning("Input Error", "Template URL must not be empty and must contain '#'.", parent=self)
            return
        
        try:
            start_num = int(start_num_str)
            end_num = int(end_num_str)
            if start_num > end_num:
                messagebox.showwarning("Input Error", "Start Number cannot be greater than End Number.", parent=self)
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Start and End Numbers must be valid integers.", parent=self)
            return
        
        if num_digits_str:
            try:
                num_digits = int(num_digits_str)
                if num_digits <= 0:
                     messagebox.showwarning("Input Error", "Number of Digits must be a positive integer.", parent=self)
                     return
            except ValueError:
                messagebox.showwarning("Input Error", "Number of Digits must be a valid integer or left empty.", parent=self)
                return
        else:
            num_digits = None

        self.result = (template_url, start_num, end_num, num_digits)
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class DownloadManager:
    """Manages download operations, including handling queues, progress, and different download types."""
    def __init__(self):
        self.download_queue = Queue()   # Queue for pending downloads
        self.active_downloads = {}        # Dictionary to store info about active downloads
        self.completed_downloads = []   # List of completed download info
        self.failed_downloads = []        # List of failed download info
        self.stop_flag = False            # Flag to signal stopping all downloads
        self.pause_flag = False           # Flag to signal pausing all downloads
        self.custom_filenames = {}        # Stores custom filenames set by user for specific URLs
        self.batch_filename_prefix = None # Prefix for sequential batch naming
        self.executor = ThreadPoolExecutor(max_workers=5) # Thread pool for concurrent downloads

    def set_custom_filename(self, url, filename):
        """Sets a custom filename for a given URL."""
        self.custom_filenames[url] = filename

    def set_batch_filename_prefix(self, prefix):
        """Sets a prefix for batch naming of files."""
        self.batch_filename_prefix = prefix

    def add_to_queue(self, urls_with_assigned_filenames_and_paths):
        """
        Adds URLs to the download queue.
        Each item is a tuple: (url, assigned_filename, save_path, is_youtube).
        """
        for url, assigned_filename, save_path, is_youtube in urls_with_assigned_filenames_and_paths:
            self.download_queue.put((url, assigned_filename, save_path, is_youtube))

    def get_proper_extension(self, url):
        """
        Attempts to determine the correct file extension for a given URL
        by looking at the URL path and Content-Type header.
        """
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Try to get extension from URL path first
        _, ext_from_path = os.path.splitext(path)
        if ext_from_path and len(ext_from_path) <= 5 and '.' in ext_from_path:   
            return ext_from_path.lower()

        url_lower = url.lower()
        
        # Prioritize common video/audio/subtitle extensions based on common patterns in URL
        if 'mp4' in url_lower and '.mp4' not in url_lower: return '.mp4'   
        if 'avi' in url_lower and '.avi' not in url_lower: return '.avi'
        if 'mov' in url_lower and '.mov' not in url_lower: return '.mov'
        if 'mkv' in url_lower and '.mkv' not in url_lower: return '.mkv'
        if 'webm' in url_lower and '.webm' not in url_lower: return '.webm'
        if 'mp3' in url_lower and '.mp3' not in url_lower: return '.mp3'
        
        # Subtitle extensions
        if 'srt' in url_lower and '.srt' not in url_lower: return '.srt'
        if 'sub' in url_lower and '.sub' not in url_lower: return '.sub'
        if 'vtt' in url_lower and '.vtt' not in url_lower: return '.vtt'

        # Other common document/image/archive types
        if 'pdf' in url_lower and '.pdf' not in url_lower: return '.pdf'
        if 'zip' in url_lower and '.zip' not in url_lower: return '.zip'
        if 'jpg' in url_lower or 'jpeg' in url_lower: return '.jpg'
        if 'png' in url_lower and '.png' not in url_lower: return '.png'
        if 'gif' in url_lower and '.gif' not in url_lower: return '.gif'

        # Fallback to Content-Type header if URL path or common patterns don't yield an extension
        try:
            # Use requests.head to get content type without downloading the whole file
            response = requests.head(url, allow_redirects=True, timeout=5) # Increased timeout
            response.raise_for_status()   # Raise HTTPError for bad responses (4xx or 5xx)
            content_type = response.headers.get('Content-Type', '').lower()
            
            if 'video/mp4' in content_type: return '.mp4'
            elif 'video/webm' in content_type: return '.webm'
            elif 'video/' in content_type: return '.mp4'   # Generic video fallback
            elif 'audio/mpeg' in content_type: return '.mp3'
            elif 'audio/' in content_type: return '.mp3'   # Generic audio fallback
            elif 'text/vtt' in content_type: return '.vtt'
            elif 'application/x-subrip' in content_type or 'text/srt' in content_type: return '.srt'
            elif 'image/jpeg' in content_type: return '.jpg'
            elif 'image/png' in content_type: return '.png'
            elif 'image/gif' in content_type: return '.gif'
            elif 'application/pdf' in content_type: return '.pdf'
            elif 'application/zip' in content_type or 'application/x-zip-compressed' in content_type: return '.zip'
            elif 'application/json' in content_type: return '.json'
            elif 'text/html' in content_type: return '.html'
            elif 'text/csv' in content_type: return '.csv'
            
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not get Content-Type for {url}: {e}") # Log the error
            pass   

        return '.bin' # Default binary extension if nothing else found

    def is_youtube_url(self, url):
        """Checks if the URL is a YouTube URL by looking at common YouTube domains."""
        youtube_domains = [
            'youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be', 'www.youtu.be',
            'youtube-nocookie.com', 'www.youtube-nocookie.com'
        ]
        parsed_url = urlparse(url)
        # Check if the netloc (domain) contains any of the YouTube domains
        return any(domain in parsed_url.netloc for domain in youtube_domains)

    def download_youtube_video(self, url, filename, save_path, quality_setting="best"):
        """
        Downloads a YouTube video using yt-dlp, providing progress updates.
        This function runs in a separate thread.
        `quality_setting` determines the format string passed to yt-dlp.
        """
        # yt-dlp automatically adds the correct extension, so we pass the base filename
        filepath_without_ext = os.path.join(save_path, os.path.splitext(filename)[0])
        
        # yt-dlp format selection based on quality_setting
        # 'bestvideo+bestaudio/best' is default, ensures separate streams are merged for best quality
        # 'best' is general best (video+audio if available)
        # 'worst' is lowest quality
        # 'mp4' specific - could add others like 'webm', 'mp3' etc.
        format_string = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" # Default best mp4
        if quality_setting == "Best":
            format_string = "bestvideo+bestaudio/best"
        elif quality_setting == "High (1080p)":
            format_string = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best"
        elif quality_setting == "Medium (720p)":
            format_string = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best"
        elif quality_setting == "Low (480p)":
            format_string = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best"
        elif quality_setting == "Audio Only":
            format_string = "bestaudio[ext=m4a]/bestaudio" # mp3 might require ffmpeg post-processing

        command = [
            'yt-dlp',
            '-f', format_string, # Format selection
            '-o', f'{filepath_without_ext}.%(ext)s', 
            '--no-playlist', 
            url
        ]
        
        self.active_downloads[url] = {
            'progress': 0, 
            'speed': 0, 
            'size': 0, 
            'filename': filename, 
            'downloaded_bytes': 0, 
            'is_youtube': True,
            'quality': quality_setting # Store quality setting
        }

        process = None 
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            total_size = 0
            downloaded_bytes = 0
            start_time = time.time()

            for line in process.stdout:
                if self.stop_flag:
                    if process: 
                        process.terminate() 
                        process.wait(timeout=1) 
                    return {'status': 'stopped', 'filename': filename, 'url': url}
                
                if self.pause_flag:
                    while self.pause_flag and not self.stop_flag:
                        time.sleep(0.1) 
                    if self.stop_flag: 
                        if process:
                            process.terminate()
                            process.wait(timeout=1)
                        return {'status': 'stopped', 'filename': filename, 'url': url}

                if "%" in line and ("[download]" in line or "[info]" in line) and ("of" in line or "at" in line):
                    try:
                        parts = line.split()
                        progress = 0.0
                        size_val = 0.0
                        size_unit = ""
                        speed_val = 0.0
                        speed_unit = ""

                        for i, part in enumerate(parts):
                            if '%' in part:
                                progress = float(part.strip('%'))
                                break
                        
                        for i, part in enumerate(parts):
                            if 'of' in part and i + 1 < len(parts):
                                size_str = parts[i + 1]
                                num_str = "".join(filter(lambda c: c.isdigit() or c == '.', size_str))
                                unit_str = "".join(filter(str.isalpha, size_str))
                                if num_str:
                                    size_val = float(num_str)
                                    size_unit = unit_str
                                break
                        
                        for i, part in enumerate(parts):
                            if 'at' in part and i + 1 < len(parts):
                                speed_str = parts[i + 1]
                                num_str = "".join(filter(lambda c: c.isdigit() or c == '.', speed_str))
                                unit_str = "".join(filter(str.isalpha, speed_str))
                                if num_str:
                                    speed_val = float(num_str)
                                    speed_unit = unit_str
                                break
                        
                        total_size = self._parse_size_string(size_val, size_unit)
                        download_speed = self._parse_size_string(speed_val, speed_unit)
                        
                        if total_size > 0:
                            downloaded_bytes = total_size * (progress / 100)
                        else:
                            downloaded_bytes = 0

                        self.active_downloads[url]['progress'] = progress
                        self.active_downloads[url]['speed'] = download_speed
                        self.active_downloads[url]['size'] = total_size
                        self.active_downloads[url]['downloaded_bytes'] = downloaded_bytes
                            
                    except (ValueError, IndexError):
                        pass 

                elif '[download] Destination:' in line: 
                    try:
                        actual_filepath = line.split('Destination:')[1].strip()
                        actual_filename = os.path.basename(actual_filepath)
                        self.active_downloads[url]['filename'] = actual_filename
                    except IndexError:
                        pass 

            process.wait() 

            if process.returncode == 0:
                found_file = None
                final_saved_filename = filename 

                if 'filename' in self.active_downloads[url]:
                    potential_actual_path = os.path.join(save_path, self.active_downloads[url]['filename'])
                    if os.path.exists(potential_actual_path):
                        found_file = potential_actual_path

                if not found_file:
                    initial_basename = os.path.splitext(filename)[0]
                    for f in os.listdir(save_path):
                        if f.startswith(initial_basename) and (f.endswith('.mp4') or f.endswith('.webm') or f.endswith('.mkv') or f.endswith('.mp3') or f.endswith('.ogg') or f.endswith('.avi') or f.endswith('.m4a')):
                            found_file = os.path.join(save_path, f)
                            break
                
                actual_size = 0
                if found_file and os.path.exists(found_file):
                    actual_size = os.path.getsize(found_file)
                    final_saved_filename = os.path.basename(found_file)
                else:
                    actual_size = downloaded_bytes

                download_info = {
                    'status': 'completed', 
                    'filename': final_saved_filename, 
                    'url': url,
                    'size': actual_size, 
                    'time': time.time() - start_time
                }
                self.completed_downloads.append(download_info)
                self.active_downloads.pop(url, None) 
                return download_info
            else:
                stderr_output = process.stderr.read() if process.stderr else "No stderr output"
                raise Exception(f"yt-dlp exited with error code {process.returncode}. Error: {stderr_output.strip()}")

        except Exception as e:
            error_info = {
                'status': 'failed', 'filename': filename, 'url': url, 'error': str(e)
            }
            self.failed_downloads.append(error_info)
            self.active_downloads.pop(url, None)
            
            initial_basename_no_ext = os.path.splitext(filename)[0]
            for f in os.listdir(save_path):
                if f.startswith(initial_basename_no_ext) and ('.part' in f or '.temp' in f or '.ytdl' in f): 
                    try:
                        os.remove(os.path.join(save_path, f))
                    except OSError as remove_err:
                        print(f"Error removing partial file {f}: {remove_err}")
            return error_info

    def _parse_size_string(self, value, unit):
        """Helper to convert string sizes (e.g., '10.0MiB') to bytes."""
        unit = unit.strip().lower()
        if unit.startswith('k'):
            return value * 1024
        elif unit.startswith('m'):
            return value * 1024**2
        elif unit.startswith('g'):
            return value * 1024**3
        elif unit.startswith('t'):
            return value * 1024**4
        return value 


    def download_file(self, url, filename, save_path):
        """
        Downloads a regular file from a URL using requests, providing progress updates.
        This function runs in a separate thread.
        """
        filepath = ""   
        try:
            filepath = os.path.join(save_path, filename) 

            if os.path.exists(filepath):
                return {'status': 'exists', 'filename': filename, 'url': url}

            self.active_downloads[url] = {
                'progress': 0, 
                'speed': 0, 
                'size': 0, 
                'filename': filename, 
                'downloaded_bytes': 0, 
                'is_youtube': False
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            start_time = time.time()

            with requests.get(url, stream=True, headers=headers, timeout=10) as r: 
                r.raise_for_status()   
                total_size = int(r.headers.get('content-length', 0)) 
                self.active_downloads[url]['size'] = total_size   

                downloaded_bytes = 0
                self.active_downloads[url]['downloaded_bytes'] = downloaded_bytes
                
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):   
                        if self.stop_flag:
                            if os.path.exists(filepath): os.remove(filepath) 
                            return {'status': 'stopped', 'filename': filename, 'url': url}
                        if self.pause_flag:
                            while self.pause_flag and not self.stop_flag:
                                time.sleep(0.1)   
                            if self.stop_flag: 
                                if os.path.exists(filepath): os.remove(filepath)
                                return {'status': 'stopped', 'filename': filename, 'url': url}
                        
                        if chunk:   
                            f.write(chunk)
                            
                            downloaded_bytes = f.tell()   
                            elapsed_time = time.time() - start_time
                            download_speed = downloaded_bytes / (elapsed_time + 0.0001) if elapsed_time > 0 else 0
                            progress = (downloaded_bytes / total_size) * 100 if total_size > 0 else 0
                            
                            self.active_downloads[url]['progress'] = progress
                            self.active_downloads[url]['speed'] = download_speed
                            self.active_downloads[url]['downloaded_bytes'] = downloaded_bytes   

            download_info = {
                'status': 'completed', 'filename': filename, 'url': url,
                'size': total_size, 'time': time.time() - start_time
            }
            self.completed_downloads.append(download_info)
            self.active_downloads.pop(url, None)
            
            if download_info['size'] == 0:   
                download_info['size'] = downloaded_bytes   

            return download_info
            
        except Exception as e:
            error_info = {
                'status': 'failed', 'filename': filename, 'url': url, 'error': str(e)
            }
            self.failed_downloads.append(error_info)
            self.active_downloads.pop(url, None)
            if os.path.exists(filepath):   
                os.remove(filepath)
            return error_info

    def start_downloads(self):
        """Starts processing items from the download queue."""
        self.stop_flag = False
        self.pause_flag = False
        while not self.download_queue.empty() and not self.stop_flag:
            url, assigned_filename, save_path, is_youtube = self.download_queue.get()
            if is_youtube:
                quality_setting = DownloaderApp.get_instance().youtube_quality_var.get()
                self.executor.submit(self.download_youtube_video, url, assigned_filename, save_path, quality_setting)
            else:
                self.executor.submit(self.download_file, url, assigned_filename, save_path)
        

    def pause_downloads(self):
        """Sets the pause flag to true, stopping current downloads temporarily."""
        self.pause_flag = True

    def resume_downloads(self):
        """Resets the pause flag to false, resuming downloads."""
        self.pause_flag = False

    def stop_all_downloads(self):
        """Sets the stop flag to true, signaling all active downloads to stop."""
        self.stop_flag = True
        self.pause_flag = False 

    @staticmethod
    def get_filename_from_url(url):
        """Extracts a default filename from a URL."""
        parsed = urlparse(url)
        path = parsed.path
        filename = os.path.basename(unquote(path)) 
        if not filename:
            filename = f"downloaded_file_{int(time.time())}" 
        return filename
    
    @staticmethod
    def get_base_name_from_url(url):
        """
        Extracts the filename without extension from a URL, cleaning up query params/fragments.
        """
        filename = DownloadManager.get_filename_from_url(url)
        filename = filename.split('?')[0].split('#')[0]
        return os.path.splitext(filename)[0] 

    @staticmethod
    def format_size(size_bytes):
        """Formats bytes into human-readable units (KB, MB, GB)."""
        if size_bytes == 0: return "0B"
        size_name = ("B", "KB", "MB", "GB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 1)
        return f"{s}{size_name[i]}"

    @staticmethod
    def format_speed(speed_bytes):
        """Formats bytes per second into human-readable speed units."""
        return f"{DownloadManager.format_size(speed_bytes)}/s"

    def generate_numbered_urls(self, template_url, start_num, end_num, num_digits=None):
        """
        Generates a list of URLs based on a template, start/end numbers, and padding.
        Replaces '#' in the template with sequentially numbered values.
        """
        generated_urls = []
        for i in range(start_num, end_num + 1):
            if num_digits is not None:
                # Format number with leading zeros (e.g., 1 -> 001 if num_digits=3)
                num_str = str(i).zfill(num_digits)
            else:
                num_str = str(i)
            
            # Replace all occurrences of '#' in the template URL
            # For simplicity, assuming '#' represents the sequential number.
            # If multiple '#' exist, they will all be replaced.
            generated_url = template_url.replace('#', num_str)
            generated_urls.append(generated_url)
        return generated_urls


class DownloaderApp:
    """The main Tkinter application class for the Download Manager GUI."""
    _instance = None # Class variable to hold the single instance (Singleton pattern)

    @staticmethod
    def get_instance():
        """Returns the single instance of DownloaderApp."""
        return DownloaderApp._instance

    def __init__(self, root):
        if DownloaderApp._instance is not None:
            # Raise an error if trying to create a second instance (enforces Singleton)
            raise Exception("DownloaderApp is a Singleton! Use DownloaderApp.get_instance()")
        DownloaderApp._instance = self # Store the single instance

        self.root = root
        self.root.title("Advanced Download Manager")   
        self.root.geometry("850x650")   
        self.root.resizable(True, True)   

        # Define fonts, with fallbacks for cross-platform compatibility
        try:
            self.default_font = Font(family="Berlin Sans Demi", size=9)   
            self.heading_font = Font(family="Berlin Sans Demi", size=10, weight="bold")   
            self.large_heading_font = Font(family="Berlin Sans Demi", size=12, weight="bold")   
            self.button_font = Font(family="Berlin Sans Demi", size=10, weight="bold")   
        except:
            self.default_font = Font(family="Segoe UI", size=9)   
            self.heading_font = Font(family="Segoe UI", size=10, weight="bold")   
            self.large_heading_font = Font(family="Segoe UI", size=12, weight="bold")   
            self.button_font = Font(family="Segoe UI Semibold", size=10, weight="bold")   

        self.fonts_dict = {
            'default': self.default_font,
            'heading': self.heading_font,
            'large_heading': self.large_heading_font,
            'button': self.button_font   
        }

        # Color palette definition for custom styling
        self.color_text_color = '#F7F8FF'
        self.color_bg_color = '#162B4A'
        self.color_accent_color = '#006EE5'
        self.color_entry_field_bg = '#D7E5FF'
        self.color_entry_text_color = self.color_bg_color
        self.color_button_text_color = '#FFFFFF' 
        self.color_disabled_color_fg = '#BDC3C7'
        self.color_hover_color = '#004CAF'
        
        self.exit_red_hover = '#FF0000'   
        self.exit_yellow_hover = '#FFD700'   
        self.exit_white_text = '#FFFFFF'
        self.exit_dark_text_on_yellow = self.color_bg_color   

        self.colors_dict = {
            'text_color': self.color_text_color,
            'bg_color': self.color_bg_color,
            'accent_color': self.color_accent_color,
            'entry_field_bg': self.color_entry_field_bg,
            'entry_text_color': self.color_entry_text_color,
            'button_text_color': self.color_button_text_color,
            'disabled_color_fg': self.color_disabled_color_fg,
            'hover_color': self.color_hover_color,
        }

        # Apply the custom theme to the root window
        try:
            CustomTheme.apply(root, self.fonts_dict)
        except Exception as e:
            print(f"Error applying theme: {e}") 
        
        self.download_manager = DownloadManager()

        # YouTube Quality Variable and options for the menubar
        self.youtube_quality_options = ["Best", "High (1080p)", "Medium (720p)", "Low (480p)", "Audio Only"]
        self.youtube_quality_var = tk.StringVar(value=self.youtube_quality_options[0]) # Default quality

        self.create_widgets()   # Create the main GUI widgets
        self.create_menubar()   # Create the menubar

        # Start periodic update of download status
        self.update_interval = 500 # milliseconds
        self.root.after(self.update_interval, self.update_download_status)

    def create_menubar(self):
        """Creates the application's menubar with File and Options menus."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.on_exit_button_click_menu)

        # Options Menu
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=options_menu)

        # YouTube Quality Submenu
        quality_menu = tk.Menu(options_menu, tearoff=0)
        options_menu.add_cascade(label="YouTube Quality", menu=quality_menu)
        
        for option in self.youtube_quality_options:
            quality_menu.add_radiobutton(label=option, variable=self.youtube_quality_var, value=option)

        # New: Numbered Batch Download Option
        options_menu.add_command(label="Numbered Batch Download...", command=self.create_batch_download_dialog)

    def on_exit_button_click_menu(self):
        """Wrapper for exit button click logic when called from menubar."""
        # Calls the existing exit logic, passing None as event object since it's from menu
        self.on_exit_button_click(None) 

    def create_batch_download_dialog(self):
        """Opens the dialog for numbered batch downloads."""
        dialog = BatchDownloadDialog(self.root, self.fonts_dict, self.colors_dict)
        if dialog.result:
            template_url, start_num, end_num, num_digits = dialog.result
            self.process_batch_urls(template_url, start_num, end_num, num_digits)

    def process_batch_urls(self, template_url, start_num, end_num, num_digits):
        """
        Generates URLs based on batch download input and adds them to the main URL input and queue.
        """
        generated_urls = self.download_manager.generate_numbered_urls(
            template_url, start_num, end_num, num_digits
        )

        if not generated_urls:
            messagebox.showwarning("Batch Download", "No URLs were generated. Please check your input.", parent=self.root)
            return

        # Append generated URLs to the existing URL input area
        current_urls_text = self.url_text.get("1.0", tk.END).strip()
        if current_urls_text: # Add newline if there's already content
            current_urls_text += "\n"
        self.url_text.delete("1.0", tk.END) # Clear existing to write new set cleanly
        self.url_text.insert("1.0", current_urls_text + "\n".join(generated_urls))
        
        messagebox.showinfo("Batch Download", f"Generated {len(generated_urls)} URLs and added them to the input list.", parent=self.root)
        
        # Automatically add the URLs to the queue and treeview
        self.add_urls()


    def create_widgets(self):
        """Initializes and arranges all GUI widgets."""
        header_frame = ttk.Frame(self.root, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(2, 2), padx=5)   
        
        ttk.Label(header_frame, text="Advanced Download Manager - created by Nima-Ghaffari",   
                  font=self.large_heading_font, anchor=tk.CENTER).pack(fill=tk.X)

        main_content_frame = ttk.Frame(self.root, style='TFrame', padding=2)   
        main_content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)   
        main_content_frame.grid_columnconfigure(0, weight=1)   
        main_content_frame.grid_rowconfigure(3, weight=1) 

        ttk.Label(main_content_frame, text="URL Input", font=self.heading_font, anchor=tk.W, style='DownloadsHeading.TLabel').grid(row=0, column=0, sticky='w', padx=5, pady=(2,0))   

        input_container_frame = ttk.Frame(main_content_frame, style='TFrame', padding=5, relief='solid', borderwidth=1)   
        input_container_frame.grid(row=1, column=0, sticky='nsew', pady=(0,2))   
        input_container_frame.grid_columnconfigure(0, weight=1)

        save_path_frame = ttk.Frame(input_container_frame, style='TFrame')   
        save_path_frame.pack(fill=tk.X, pady=(0,2))   
        save_path_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(save_path_frame, text="Save to:", font=self.default_font).pack(side=tk.LEFT, padx=(0,2))   
        self.save_path_var = tk.StringVar(value=os.path.expanduser("~/Downloads")) 
        self.path_entry = ttk.Entry(save_path_frame, textvariable=self.save_path_var, font=self.default_font)   
        self.path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,2))   
        ttk.Button(save_path_frame, text="Browse", command=self.browse_path, width=8).pack(side=tk.LEFT)

        ttk.Label(input_container_frame, text="Enter URLs (one per line):", font=self.default_font).pack(anchor=tk.W, pady=(2,2))   
        self.url_text = scrolledtext.ScrolledText(input_container_frame, height=6, wrap=tk.WORD, font=self.default_font, undo=True)
        self.url_text.pack(fill=tk.BOTH, expand=True, pady=(0, 2))   

        input_buttons_frame = ttk.Frame(input_container_frame, style='TFrame')   
        input_buttons_frame.pack(fill=tk.X, pady=(0,2), anchor=tk.W)   
        
        fixed_button_width = 15   

        self.add_btn = ttk.Button(input_buttons_frame, text="Add URLs", command=self.add_urls, width=fixed_button_width)   
        self.add_btn.pack(side=tk.LEFT, padx=(0,1))   
        
        ttk.Button(input_buttons_frame, text="Set Names", command=self.set_filenames, width=fixed_button_width).pack(side=tk.LEFT, padx=(0,1))   
        ttk.Button(input_buttons_frame, text="Reset Names", command=self.reset_filenames, width=fixed_button_width).pack(side=tk.LEFT, padx=(0,1))   

        self.use_subfolder_var = tk.IntVar(value=0)
        self.subfolder_var = tk.StringVar(value="")

        self.subfolder_checkbox = tk.Checkbutton(
            input_buttons_frame, 
            text="Save custom folder:",   
            variable=self.use_subfolder_var,
            command=self.toggle_subfolder_entry,
            font=self.default_font,   
            bg=self.color_bg_color,
            fg=self.color_text_color,
            selectcolor=self.color_bg_color, 
            activebackground=self.color_bg_color,
            activeforeground=self.color_text_color,
            highlightbackground=self.color_bg_color,
            highlightcolor=self.color_bg_color,
            borderwidth=0,
            indicatoron=True 
        )
        self.subfolder_checkbox.pack(side=tk.LEFT, padx=(5, 5)) 

        self.subfolder_entry = ttk.Entry(
            input_buttons_frame, 
            textvariable=self.subfolder_var,
            font=self.default_font,
            state=tk.DISABLED, 
            width=20 
        )
        self.subfolder_entry.pack(side=tk.LEFT, expand=False, fill=tk.X, padx=(0,2))   
        
        self.confirm_subfolder_btn = ttk.Button(
            input_buttons_frame, 
            text="Confirm",
            command=self.confirm_subfolder_selection,
            state=tk.DISABLED, 
            width=8 
        )
        self.confirm_subfolder_btn.pack(side=tk.LEFT, padx=(0,0))   

        ttk.Label(main_content_frame, text="Downloads", font=self.heading_font, anchor=tk.W, style='DownloadsHeading.TLabel').grid(row=2, column=0, sticky='w', padx=5, pady=(2,0))   

        downloads_list_container_frame = ttk.Frame(main_content_frame, style='TFrame', padding=5, relief='solid', borderwidth=1)   
        downloads_list_container_frame.grid(row=3, column=0, sticky='nsew', pady=(0,5))   
        downloads_list_container_frame.grid_rowconfigure(0, weight=1)
        downloads_list_container_frame.grid_columnconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(downloads_list_container_frame, columns=('filename', 'size', 'progress', 'status'), show='headings')   
        
        self.tree.heading('filename', text='Filename')   
        self.tree.heading('size', text='Size')
        self.tree.heading('progress', text='Progress / Speed')   
        self.tree.heading('status', text='Status')
        
        self.tree.column('filename', width=280, anchor=tk.W)   
        self.tree.column('size', width=90, anchor=tk.E)   
        self.tree.column('progress', width=120, anchor=tk.E)   
        self.tree.column('status', width=100, anchor=tk.W)   
        
        y_scroll = ttk.Scrollbar(downloads_list_container_frame, orient='vertical', command=self.tree.yview)
        x_scroll = ttk.Scrollbar(downloads_list_container_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, sticky='ew')

        left_control_buttons_frame = ttk.Frame(self.root, style='TFrame', padding=(2, 2))   
        left_control_buttons_frame.pack(side=tk.LEFT, anchor=tk.SW, padx=5, pady=(2, 5))   

        self.start_btn = ttk.Button(left_control_buttons_frame, text="Start All", command=self.start_downloads, width=fixed_button_width)   
        self.start_btn.pack(side=tk.LEFT, padx=(0,1))   
        
        self.pause_btn = ttk.Button(left_control_buttons_frame, text="Pause / Resume", command=self.pause_toggle, state=tk.DISABLED, width=fixed_button_width)   
        self.pause_btn.pack(side=tk.LEFT, padx=(0,1))   
        
        self.stop_btn = ttk.Button(left_control_buttons_frame, text="Stop All", command=self.stop_downloads, width=fixed_button_width)   
        self.stop_btn.pack(side=tk.LEFT, padx=(0,1))   

        self.another_btn = ttk.Button(left_control_buttons_frame, text="Clear All", command=self.clear_all_content, width=fixed_button_width)   
        self.another_btn.pack(side=tk.LEFT, padx=(0,1))   

        right_control_buttons_frame = ttk.Frame(self.root, style='TFrame', padding=(2, 2))   
        right_control_buttons_frame.pack(side=tk.RIGHT, anchor=tk.SE, padx=5, pady=(2, 5))   

        self.exit_btn = tk.Button(right_control_buttons_frame, text="Exit",   
                                   font=self.fonts_dict['button'],   
                                   width=fixed_button_width,   
                                   bg=self.color_accent_color,   
                                   fg=self.color_button_text_color,
                                   relief=tk.FLAT, borderwidth=0, padx=10, pady=5,
                                   activebackground=self.color_hover_color,   
                                   activeforeground=self.color_button_text_color)

        self.exit_btn.pack(side=tk.RIGHT)
        
        self.exit_default_bg_color = self.color_accent_color
        self.exit_default_fg_color = self.color_button_text_color
        self.exit_default_active_bg = self.color_hover_color   
        self.exit_default_active_fg = self.color_button_text_color
        
        self.exit_btn.bind("<Enter>", self.on_exit_button_hover)
        self.exit_btn.bind("<Leave>", self.on_exit_button_leave)
        self.exit_btn.bind("<Button-1>", self.on_exit_button_click)   

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")   
        ttk.Label(self.root, textvariable=self.status_var, style='TStatus.TLabel').pack(fill=tk.X, pady=(0,0), padx=5)   

    def toggle_subfolder_entry(self):
        """Enables/disables the subfolder entry and confirm button based on checkbox state."""
        if self.use_subfolder_var.get() == 1:
            self.subfolder_entry.config(state=tk.NORMAL)
            self.confirm_subfolder_btn.config(state=tk.NORMAL)   
        else:
            self.subfolder_entry.config(state=tk.DISABLED)
            self.confirm_subfolder_btn.config(state=tk.DISABLED)   
            self.subfolder_var.set("") # Clear subfolder name if unchecked  
            self.subfolder_entry.config(style='TEntry') # Reset style if it was in error/success state 

    def confirm_subfolder_selection(self):
        """Confirms the entered subfolder name, applying validation and visual feedback."""
        if self.use_subfolder_var.get() == 1:
            subfolder_name = self.subfolder_var.get().strip()
            if not subfolder_name:
                messagebox.showwarning("Warning", "Please enter a name for the custom subfolder before confirming.", parent=self.root)
                self.subfolder_entry.config(style='TEntry.Error')   
                self.root.after(1000, lambda: self.subfolder_entry.config(style='TEntry'))   
                return

            sanitized_name = "".join(c for c in subfolder_name if c.isalnum() or c in (' ', '.', '_', '-')).strip()
            if not sanitized_name:
                messagebox.showwarning("Warning", "Invalid subfolder name. Please use alphanumeric characters, spaces, dots, underscores, or hyphens.", parent=self.root)
                self.subfolder_entry.config(style='TEntry.Error')
                self.root.after(1000, lambda: self.subfolder_entry.config(style='TEntry'))
                return
            
            self.subfolder_entry.config(style='TEntry.Success')   
            self.status_var.set(f"Subfolder '{sanitized_name}' confirmed.")
            self.root.after(1500, lambda: self.subfolder_entry.config(style='TEntry'))   
            self.subfolder_var.set(sanitized_name) 
        else:   
            self.status_var.set("Subfolder option not selected.")


    def on_exit_button_hover(self, event):
        """Changes exit button color on hover based on download status."""
        if self.download_manager.active_downloads:
            self.exit_btn.config(bg=self.exit_red_hover, fg=self.exit_white_text,   
                                         activebackground=self.exit_red_hover, activeforeground=self.exit_white_text)
        elif not self.download_manager.download_queue.empty():
            self.exit_btn.config(bg=self.exit_yellow_hover, fg=self.exit_dark_text_on_yellow,   
                                         activebackground=self.exit_yellow_hover, activeforeground=self.exit_dark_text_on_yellow)
        else:
            self.exit_btn.config(bg=self.exit_default_active_bg, fg=self.exit_default_active_fg,   
                                         activebackground=self.exit_default_active_bg, activeforeground=self.exit_default_active_fg)

    def on_exit_button_leave(self, event):
        """Resets exit button color when mouse leaves."""
        self.exit_btn.config(bg=self.exit_default_bg_color, fg=self.exit_default_fg_color,   
                                       activebackground=self.exit_default_active_bg, activeforeground=self.exit_default_active_fg)


    def on_exit_button_click(self, event):
        """Handles exit button click with confirmation for ongoing downloads."""
        if self.download_manager.active_downloads:
            response = messagebox.askyesno("Confirm Exit",   
                                            "Downloads are in progress. Do you want to stop all downloads and exit?",
                                            parent=self.root, icon='warning')
            if response:
                self.download_manager.stop_all_downloads()
                self.root.quit()   
        elif not self.download_manager.download_queue.empty():
            response = messagebox.askyesno("Confirm Exit",   
                                            "There are pending downloads in the queue. Do you want to clear the queue and exit?",
                                            parent=self.root, icon='question')
            if response:
                self.download_manager.stop_all_downloads()   
                with self.download_manager.download_queue.mutex:
                    self.download_manager.download_queue.queue.clear()
                self.root.quit()
        else:
            self.root.quit()

    def set_filenames(self):
        """Prompts user to set a batch filename prefix for all URLs."""
        urls_text = self.url_text.get("1.0", tk.END).strip()
        if not urls_text:
            messagebox.showwarning("Warning", "Please enter URLs first to set filenames.", parent=self.root)
            return

        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        if not urls:
            messagebox.showwarning("Warning", "No valid URLs found to set filenames for.", parent=self.root)
            return

        dialog = CustomFilenameDialog(self.root, "Set Base Filename", 
                                            "Enter base name for files (e.g., 'MyMovie'):", 
                                            "MyFile", 
                                            self.fonts_dict, self.colors_dict)
        base_name = dialog.result
        
        if base_name:
            self.download_manager.set_batch_filename_prefix(base_name)
            self.download_manager.custom_filenames = {} 
            self.update_treeview_filenames()   
        else:
            self.download_manager.batch_filename_prefix = None 
            self.update_treeview_filenames()
            messagebox.showinfo("Filename Setup", "No base name set. Filenames will revert to default URL names or individual custom names.", parent=self.root)

    def edit_filenames(self):
        """
        Allows user to edit filenames for each URL individually.
        (Note: This function is present in the DownloadManager but not currently hooked to a GUI button).
        """
        urls_text = self.url_text.get("1.0", tk.END).strip()
        if not urls_text:
            messagebox.showwarning("Warning", "Please enter URLs first to set individual filenames.", parent=self.root)
            return
            
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        for url in urls:
            default_name = self.download_manager.get_filename_from_url(url)
            ext = self.download_manager.get_proper_extension(url)
            if not default_name.lower().endswith(ext) and '.' not in default_name:
                default_name += ext

            dialog = CustomFilenameDialog(self.root, "Edit Filename",
                                                 f"Enter name for:\n{url}", 
                                                 default_name,
                                                 self.fonts_dict, self.colors_dict)
            new_name = dialog.result

            if new_name:
                if '.' not in new_name or new_name.endswith('.'):   
                    new_name += self.download_manager.get_proper_extension(url)
                self.download_manager.set_custom_filename(url, new_name)
        
        self.update_treeview_filenames()   

    def reset_filenames(self):
        """Resets all custom and batch filenames to default (derived from URL)."""
        self.download_manager.custom_filenames = {}
        self.download_manager.batch_filename_prefix = None
        messagebox.showinfo("Reset", "Filenames reset to default (derived from URL).", parent=self.root)
        self.update_treeview_filenames()   

    def update_treeview_filenames(self):
        """
        Populates or updates the Treeview with URLs and their determined filenames.
        Also, prepares the download queue with final filenames and save paths.
        This function determines if a URL is YouTube or not and assigns filenames.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        urls_text = self.url_text.get("1.0", tk.END).strip()
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]

        processed_urls_for_queue = []
        
        extension_counters = {} 

        base_save_path = self.save_path_var.get()
        final_save_path = base_save_path

        if self.use_subfolder_var.get() == 1:   
            subfolder_name = self.subfolder_var.get().strip()
            if subfolder_name: 
                final_save_path = os.path.join(base_save_path, subfolder_name)
            
        for url in urls:
            filename_to_display = ""
            assigned_filename_for_queue = ""
            is_youtube = self.download_manager.is_youtube_url(url) 

            if url in self.download_manager.custom_filenames:
                filename_to_display = self.download_manager.custom_filenames[url]
                assigned_filename_for_queue = filename_to_display
            elif self.download_manager.batch_filename_prefix:
                current_ext = ".mp4" if is_youtube else self.download_manager.get_proper_extension(url)
                
                current_counter = extension_counters.get(current_ext, 0)
                current_counter += 1 
                extension_counters[current_ext] = current_counter 

                filename_to_display = f"{self.download_manager.batch_filename_prefix}_{current_counter:03d}{current_ext}"
                assigned_filename_for_queue = filename_to_display
            else:
                filename_to_display = self.download_manager.get_filename_from_url(url)
                if not is_youtube: 
                    ext = self.download_manager.get_proper_extension(url)
                    if not filename_to_display.lower().endswith(ext) and '.' not in filename_to_display:
                        filename_to_display += ext
                assigned_filename_for_queue = filename_to_display

            self.tree.insert('', 'end', values=(filename_to_display, '', '0%', 'Ready'), iid=url) 
            processed_urls_for_queue.append((url, assigned_filename_for_queue, final_save_path, is_youtube))
        
        with self.download_manager.download_queue.mutex:
            self.download_manager.download_queue.queue.clear()
        self.download_manager.add_to_queue(processed_urls_for_queue)

    def browse_path(self):
        """Opens a directory dialog for the user to select a save path."""
        path = filedialog.askdirectory(parent=self.root)
        if path:
            self.save_path_var.set(path)

    def add_urls(self):
        """Adds URLs from the text input to the download queue and updates the Treeview."""
        urls_text = self.url_text.get("1.0", tk.END).strip()
        if not urls_text:
            messagebox.showwarning("Warning", "Please enter at least one URL to add.", parent=self.root)
            return
            
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        urls = [url for url in urls if url] 

        if not urls: 
            messagebox.showwarning("Warning", "No valid URLs found to add.", parent=self.root)
            return

        base_save_path = self.save_path_var.get()
        final_save_path = base_save_path

        if self.use_subfolder_var.get() == 1:   
            subfolder_name = self.subfolder_var.get().strip()
            if not subfolder_name:   
                messagebox.showwarning("Warning", "Please enter a name for the custom subfolder.", parent=self.root)
                self.subfolder_entry.config(style='TEntry.Error')
                self.root.after(1000, lambda: self.subfolder_entry.config(style='TEntry'))
                return
            
            sanitized_name = "".join(c for c in subfolder_name if c.isalnum() or c in (' ', '.', '_', '-')).strip()
            if not sanitized_name:
                messagebox.showwarning("Warning", "Invalid subfolder name. Please use alphanumeric characters, spaces, dots, underscores, or hyphens.", parent=self.root)
                self.subfolder_entry.config(style='TEntry.Error')
                self.root.after(1000, lambda: self.subfolder_entry.config(style='TEntry'))
                return
            
            final_save_path = os.path.join(base_save_path, sanitized_name)   
        
        if not os.path.exists(final_save_path):
            try:
                os.makedirs(final_save_path, exist_ok=True)
            except OSError as e:
                messagebox.showerror("Error", f"Could not create save directory: {e}", parent=self.root)
                return
        
        self.update_treeview_filenames() 
        
        self.url_text.delete("1.0", tk.END) 
        self.status_var.set(f"Added {len(urls)} URLs to queue. Ready to start downloads.")   

    def start_downloads(self):
        """Initiates the download process for all queued items."""
        if self.download_manager.download_queue.empty() and not self.download_manager.active_downloads:
            messagebox.showwarning("Warning", "No files in queue or active downloads to start.", parent=self.root)
            return
            
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL, text="Pause / Resume")   
        self.stop_btn.config(state=tk.NORMAL)
        self.add_btn.config(state=tk.DISABLED)   
        self.another_btn.config(state=tk.DISABLED)   
        self.confirm_subfolder_btn.config(state=tk.DISABLED)   
        self.subfolder_checkbox.config(state=tk.DISABLED)   
        self.subfolder_entry.config(state=tk.DISABLED)   
        
        if self.download_manager.active_downloads or not self.download_manager.download_queue.empty():
            self.exit_btn.config(state=tk.DISABLED)   
        
        Thread(target=self.download_manager.start_downloads, daemon=True).start()
        self.status_var.set("Downloading...")   

    def pause_toggle(self):
        """Toggles between pausing and resuming downloads."""
        if self.download_manager.pause_flag:
            self.download_manager.resume_downloads()
            self.pause_btn.config(text="Pause / Resume")
            self.status_var.set("Downloading...")
        else:
            self.download_manager.pause_downloads()
            self.pause_btn.config(text="Resume")   
            self.status_var.set("Paused")   

    def stop_downloads(self):
        """Stops all active and pending downloads."""
        self.download_manager.stop_all_downloads()
        self.status_var.set("Stopping downloads...")   
        
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="Pause / Resume")
        self.stop_btn.config(state=tk.DISABLED)
        self.add_btn.config(state=tk.NORMAL)
        self.another_btn.config(state=tk.NORMAL)   
        self.exit_btn.config(state=tk.NORMAL)   
        
        if not self.download_manager.active_downloads and self.download_manager.download_queue.empty():
            self.subfolder_checkbox.config(state=tk.NORMAL)
            if self.use_subfolder_var.get() == 1:   
                self.subfolder_entry.config(state=tk.NORMAL)
                self.confirm_subfolder_btn.config(state=tk.NORMAL)

    def clear_all_content(self):
        """Clears all URLs, download status, and resets the application state."""
        self.download_manager.stop_all_downloads()
        time.sleep(0.1) 
        
        self.url_text.delete("1.0", tk.END) 

        self.tree.delete(*self.tree.get_children()) 

        self.download_manager = DownloadManager()   

        self.status_var.set("Ready for new downloads.")

        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="Pause / Resume")
        self.stop_btn.config(state=tk.DISABLED)
        self.add_btn.config(state=tk.NORMAL)
        self.another_btn.config(state=tk.NORMAL)   
        self.exit_btn.config(state=tk.NORMAL)   

        self.subfolder_checkbox.config(state=tk.NORMAL)
        self.subfolder_entry.config(state=tk.DISABLED)   
        self.confirm_subfolder_btn.config(state=tk.DISABLED)   
        self.use_subfolder_var.set(0)   
        self.subfolder_var.set("")   


    def update_download_status(self):
        """
        Periodically updates the download progress and status in the Treeview.
        Also manages button states and status bar messages.
        """
        if not all([self.start_btn, self.pause_btn, self.stop_btn, self.add_btn, self.another_btn, 
                    self.exit_btn, self.tree, self.subfolder_checkbox, self.subfolder_entry, self.confirm_subfolder_btn]):   
            self.root.after(self.update_interval, self.update_download_status)
            return

        for url, info in list(self.download_manager.active_downloads.items()): 
            item_id = url 
            
            if item_id in self.tree.get_children(): 
                display_size = ""
                display_progress_speed = ""   
                status_text = ""

                if info['size'] > 0:   
                    display_size = self.download_manager.format_size(info['size'])
                    display_progress_speed = f"{info['progress']:.1f}% ({self.download_manager.format_speed(info['speed'])})"
                    status_text = "Downloading" if not self.download_manager.pause_flag else "Paused"
                else:   
                    if info['is_youtube']:
                        display_size = "Unknown" 
                        display_progress_speed = f"{info['progress']:.1f}% ({self.download_manager.format_speed(info['speed'])})" if info['progress'] > 0 else "N/A"
                        status_text = f"Downloading (YouTube - {info.get('quality', 'Best')})" if not self.download_manager.pause_flag else f"Paused (YouTube - {info.get('quality', 'Best')})"
                    else:
                        display_size = f"{self.download_manager.format_size(info['downloaded_bytes'])} / Unknown"
                        display_progress_speed = f"N/A ({self.download_manager.format_speed(info['speed'])})"
                        status_text = "Downloading" if not self.download_manager.pause_flag else "Paused"

                self.tree.item(item_id, values=(
                    info['filename'],   
                    display_size,
                    display_progress_speed,   
                    status_text
                ))
        
        while self.download_manager.completed_downloads:
            info = self.download_manager.completed_downloads.pop(0)
            completed_size_display = self.download_manager.format_size(info['size'])   
            
            item_id = info['url'] 
            
            if item_id in self.tree.get_children() and self.tree.item(item_id, 'values')[3] != "Completed":   
                self.tree.item(item_id, values=(
                    info['filename'],
                    completed_size_display,   
                    "100%",
                    "Completed"   
                ))
                
        while self.download_manager.failed_downloads:
            info = self.download_manager.failed_downloads.pop(0)
            item_id = info['url'] 
            
            if item_id in self.tree.get_children() and not self.tree.item(item_id, 'values')[3].startswith("Error"):   
                self.tree.item(item_id, values=(
                    info['filename'],
                    "",   
                    "0%",
                    f"Error: {info['error'][:30]}..."   
                ))
        
        if not self.download_manager.active_downloads and self.download_manager.download_queue.empty():
            if self.status_var.get() not in ["Ready", "All downloads finished.", "Stopping downloads.", "Ready for new downloads."]:
                self.status_var.set("All downloads finished.")   
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED, text="Pause / Resume")
            self.stop_btn.config(state=tk.DISABLED)
            self.add_btn.config(state=tk.NORMAL)
            self.another_btn.config(state=tk.NORMAL)   
            self.exit_btn.config(state=tk.NORMAL)   

            self.subfolder_checkbox.config(state=tk.NORMAL)
            if self.use_subfolder_var.get() == 1:   
                self.subfolder_entry.config(state=tk.NORMAL)
                self.confirm_subfolder_btn.config(state=tk.NORMAL)

        elif self.download_manager.pause_flag:
            self.status_var.set("Paused")
            self.pause_btn.config(text="Resume")
        elif self.download_manager.active_downloads:
            self.status_var.set("Downloading...")
            self.pause_btn.config(text="Pause / Resume")
        elif not self.download_manager.download_queue.empty():
            self.status_var.set("Queued, awaiting start...")
            self.start_btn.config(state=tk.NORMAL)   
        
        self.on_exit_button_leave(None) 

        self.root.after(self.update_interval, self.update_download_status)


if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()