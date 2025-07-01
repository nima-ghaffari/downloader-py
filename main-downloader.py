import os
import requests
import time
import math
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, unquote
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, Menu
from threading import Thread
from queue import Queue
from tkinter.font import Font

class CustomTheme:
    @staticmethod
    def apply(root, fonts):
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

        style = ttk.Style()

        if 'clam' in style.theme_names():
            style.theme_use('clam')
        else:
            style.theme_use('default')

        style.configure('.', font=fonts['default'])
        root.configure(bg=bg_color)
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=text_color)

        style.configure('TCheckbutton',
                        font=fonts['default'],
                        background=bg_color,
                        foreground=text_color,
                        indicatoron=True,
                        padding=3)
        style.map('TCheckbutton',
                  background=[('active', bg_color)],
                  foreground=[('disabled', disabled_color_fg)])

        style.configure('TEntry.Error', fieldbackground='#FF6347', foreground='white')
        style.configure('TEntry.Success', fieldbackground='#8BC34A', foreground='white')

        style.configure('TLabelFrame',
                        background=accent_color,
                        foreground=text_color,
                        bordercolor=border_color,
                        relief='solid',
                        borderwidth=1,
                        font=fonts['heading'])
        style.map('TLabelFrame', background=[('active', accent_color)])

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

        root.option_add('*Scrolledtext*background', entry_field_bg)
        root.option_add('*Scrolledtext*foreground', entry_text_color)
        root.option_add('*Scrolledtext*insertBackground', entry_text_color)
        root.option_add('*Scrolledtext*selectBackground', selected_item_bg)
        root.option_add('*Scrolledtext*selectForeground', selected_item_text)
        root.option_add('*Scrolledtext*borderwidth', 1)
        root.option_add('*Scrolledtext*relief', 'solid')
        root.option_add('*Scrolledtext*highlightbackground', border_color)
        root.option_add('*Scrolledtext*highlightcolor', accent_color)

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

        style.configure('Treeview.Heading',
                        background=accent_color,
                        foreground=text_color,
                        relief='flat',
                        padding=5,
                        font=fonts['heading'])
        style.map('Treeview.Heading',
                  background=[('active', hover_color)])

        style.configure('TStatus.TLabel',
                        background=bg_color,
                        foreground=text_color,
                        relief='sunken',
                        padding=[5,2],
                        anchor='w')

        style.configure('DownloadsHeading.TLabel',
                        background=bg_color,
                        foreground=text_color,
                        font=fonts['heading'],
                        padding=(0, 5, 0, 2))

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

        root.option_add('*Toplevel*background', bg_color)
        root.option_add('*Dialog*background', bg_color)
        root.option_add('*Dialog*foreground', text_color)
        root.option_add('*Message*background', bg_color)
        root.option_add('*Message*foreground', text_color)
        root.option_add('*Button*background', accent_color)
        root.option_add('*Button*foreground', button_text_color)
        style.configure('Dialog.TButton', background=accent_color, foreground=button_text_color)

class CustomFilenameDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt_text, initial_value, fonts, colors):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.parent = parent
        self.result = None
        self.fonts = fonts
        self.colors = colors

        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        self.configure(bg=self.colors['bg_color'])

        self.create_widgets(prompt_text, initial_value)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.wait_window(self)

    def create_widgets(self, prompt_text, initial_value):
        prompt_label = tk.Label(self, text=prompt_text, font=self.fonts['default'],
                                fg=self.colors['text_color'], bg=self.colors['bg_color'], pady=10)
        prompt_label.pack(padx=10, pady=5)

        self.entry_var = tk.StringVar(value=initial_value)
        self.entry = ttk.Entry(self, textvariable=self.entry_var, font=self.fonts['default'], width=50)
        self.entry.pack(padx=10, pady=5, fill=tk.X)
        self.entry.bind("<Return>", lambda event: self.ok())
        self.entry.focus_set()

        button_frame = ttk.Frame(self, style='TFrame')
        button_frame.pack(pady=10)

        ok_button = ttk.Button(button_frame, text="OK", command=self.ok, width=10)
        ok_button.pack(side=tk.LEFT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel, width=10)
        cancel_button.pack(side=tk.LEFT, padx=5)

    def ok(self):
        self.result = self.entry_var.get()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

class BatchUrlGeneratorDialog(tk.Toplevel):
    """
    Dialog window to generate batch URLs from a pattern.
    """
    def __init__(self, parent, fonts, colors):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Generate Batch URLs")
        self.parent = parent
        self.result = None
        self.fonts = fonts
        self.colors = colors

        self.configure(bg=self.colors['bg_color'], padx=10, pady=10)

        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (400 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (300 // 2)
        self.geometry(f"400x250+{x}+{y}")

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.wait_window(self)

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---- Start of modified code ----
        # Clarified the instructions for zero-padding.
        ttk.Label(main_frame, text="URL Template (use ## for 01, ### for 001, etc.):", font=self.fonts['default']).pack(anchor='w', pady=(5, 2))
        # ---- End of modified code ----
        
        self.url_template_var = tk.StringVar(value="")
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_template_var, font=self.fonts['default'])
        self.url_entry.pack(fill=tk.X, expand=True, pady=(0, 10))
        self.url_entry.focus_set()

        range_frame = ttk.Frame(main_frame, style='TFrame')
        range_frame.pack(fill=tk.X, expand=True, pady=(0, 10))

        ttk.Label(range_frame, text="From:", font=self.fonts['default']).pack(side=tk.LEFT, padx=(0, 5))
        self.start_var = tk.StringVar(value="1")
        start_entry = ttk.Entry(range_frame, textvariable=self.start_var, font=self.fonts['default'], width=8)
        start_entry.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(range_frame, text="To:", font=self.fonts['default']).pack(side=tk.LEFT, padx=(0, 5))
        self.end_var = tk.StringVar(value="10")
        end_entry = ttk.Entry(range_frame, textvariable=self.end_var, font=self.fonts['default'], width=8)
        end_entry.pack(side=tk.LEFT)

        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(pady=20)

        ok_button = ttk.Button(button_frame, text="Generate", command=self.generate, width=12)
        ok_button.pack(side=tk.LEFT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel, width=12)
        cancel_button.pack(side=tk.LEFT, padx=5)

    def generate(self):
        template = self.url_template_var.get().strip()
        start_str = self.start_var.get().strip()
        end_str = self.end_var.get().strip()

        if '#' not in template:
            messagebox.showerror("Error", "URL template must contain at least one '#' character.", parent=self)
            return

        try:
            start_num = int(start_str)
            end_num = int(end_str)
        except ValueError:
            messagebox.showerror("Error", "Start and end numbers must be integers.", parent=self)
            return

        if start_num > end_num:
            messagebox.showerror("Error", "Start number cannot be greater than the end number.", parent=self)
            return

        # This logic correctly handles padding based on the number of '#' characters.
        placeholder = '#' * template.count('#')
        padding = len(placeholder)
        generated_urls = []

        for i in range(start_num, end_num + 1):
            num_str = str(i).zfill(padding)
            generated_urls.append(template.replace(placeholder, num_str))

        self.result = generated_urls
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

class DownloadManager:
    def __init__(self):
        self.download_queue = Queue()
        self.active_downloads = {}
        self.completed_downloads = []
        self.failed_downloads = []
        self.stop_flag = False
        self.pause_flag = False
        self.custom_filenames = {}
        self.batch_filename_prefix = None
        # Downloads are now sequential (one by one) to prevent server errors.
        self.executor = ThreadPoolExecutor(max_workers=1)

    def set_custom_filename(self, url, filename):
        self.custom_filenames[url] = filename

    def set_batch_filename_prefix(self, prefix):
        self.batch_filename_prefix = prefix

    def add_to_queue(self, urls_with_assigned_filenames_and_paths):
        for url, assigned_filename, save_path in urls_with_assigned_filenames_and_paths:
            self.download_queue.put((url, assigned_filename, save_path))

    def get_proper_extension(self, url, check_online=False):
        parsed_url = urlparse(url)
        path = parsed_url.path

        _, ext_from_path = os.path.splitext(path)
        if ext_from_path and len(ext_from_path) <= 5 and '.' in ext_from_path:
            return ext_from_path.lower()

        url_lower = url.lower()

        if 'mp4' in url_lower and not 'mp4.' in url_lower: return '.mp4'
        if 'avi' in url_lower and not 'avi.' in url_lower: return '.avi'
        if 'mov' in url_lower and not 'mov.' in url_lower: return '.mov'
        if 'mkv' in url_lower and not 'mkv.' in url_lower: return '.mkv'
        if 'webm' in url_lower and not 'webm.' in url_lower: return '.webm'
        if 'mp3' in url_lower and not 'mp3.' in url_lower: return '.mp3'
        if 'srt' in url_lower and not 'srt.' in url_lower: return '.srt'
        if 'sub' in url_lower and not 'sub.' in url_lower: return '.sub'
        if 'vtt' in url_lower and not 'vtt.' in url_lower: return '.vtt'
        if 'pdf' in url_lower and not 'pdf.' in url_lower: return '.pdf'
        if 'zip' in url_lower and not 'zip.' in url_lower: return '.zip'
        if 'jpg' in url_lower or 'jpeg' in url_lower: return '.jpg'
        if 'png' in url_lower and not 'png.' in url_lower: return '.png'
        if 'gif' in url_lower and not 'gif.' in url_lower: return '.gif'

        if check_online:
            try:
                response = requests.head(url, allow_redirects=True, timeout=3)
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '').lower()

                if 'video/mp4' in content_type: return '.mp4'
                elif 'video/webm' in content_type: return '.webm'
                elif 'video/' in content_type: return '.mp4'
                elif 'audio/mpeg' in content_type: return '.mp3'
                elif 'audio/' in content_type: return '.mp3'
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

            except requests.exceptions.RequestException:
                pass

        return '.bin'

    def download_file(self, url, filename, save_path):
        filepath = ""
        try:
            filepath = os.path.join(save_path, filename)

            if os.path.exists(filepath):
                return {'status': 'exists', 'filename': filename, 'url': url}

            self.active_downloads[url] = {'progress': 0, 'speed': 0, 'size': 0, 'filename': filename, 'downloaded_bytes': 0}

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            start_time = time.time()

            with requests.get(url, stream=True, headers=headers) as r:
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
            error_message = str(e)
            if isinstance(e, requests.exceptions.HTTPError):
                if e.response.status_code == 404:
                    error_message = "File not found on server (404)"
                elif e.response.status_code == 403:
                    error_message = "Access Forbidden (403)"
                else:
                    error_message = f"Server Error ({e.response.status_code})"
            
            error_info = {
                'status': 'failed', 'filename': filename, 'url': url, 'error': error_message
            }
            
            self.failed_downloads.append(error_info)
            self.active_downloads.pop(url, None)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except OSError:
                    pass
            return error_info

    def start_downloads(self):
        self.stop_flag = False
        self.pause_flag = False
        while not self.download_queue.empty() and not self.stop_flag:
            url, assigned_filename, save_path = self.download_queue.get()
            self.executor.submit(self.download_file, url, assigned_filename, save_path)

    def pause_downloads(self):
        self.pause_flag = True

    def resume_downloads(self):
        self.pause_flag = False

    def stop_all_downloads(self):
        self.stop_flag = True
        self.pause_flag = False

    @staticmethod
    def get_filename_from_url(url):
        parsed = urlparse(url)
        path = parsed.path
        filename = os.path.basename(unquote(path))
        if not filename:
            filename = f"downloaded_file_{int(time.time())}"
        return filename

    @staticmethod
    def get_base_name_from_url(url):
        filename = DownloadManager.get_filename_from_url(url)
        filename = filename.split('?')[0].split('#')[0]
        return os.path.splitext(filename)[0]

    @staticmethod
    def format_size(size_bytes):
        if size_bytes == 0: return "0B"
        size_name = ("B", "KB", "MB", "GB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 1)
        return f"{s}{size_name[i]}"

    @staticmethod
    def format_speed(speed_bytes):
        return f"{DownloadManager.format_size(speed_bytes)}/s"

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Download Manager")
        self.root.geometry("850x650")
        self.root.resizable(True, True)

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

        try:
            CustomTheme.apply(root, self.fonts_dict)
        except Exception as e:
            print(f"Error applying theme: {e}")

        self.download_manager = DownloadManager()
        self.create_widgets()
        
        self.create_menu()
        
        self.update_interval = 500
        self.root.after(self.update_interval, self.update_download_status)

    def create_menu(self):
        self.menu_bar = Menu(self.root,
            bg=self.color_bg_color,
            fg=self.color_text_color,
            activebackground=self.color_accent_color,
            activeforeground=self.color_text_color
        )
        self.root.config(menu=self.menu_bar)

        tools_menu = Menu(self.menu_bar, tearoff=0,
            bg=self.color_bg_color,
            fg=self.color_text_color,
            activebackground=self.color_hover_color,
            activeforeground=self.color_text_color
        )
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Generate Batch URLs", command=self.open_batch_url_generator)

    def open_batch_url_generator(self):
        dialog = BatchUrlGeneratorDialog(self.root, self.fonts_dict, self.colors_dict)
        if dialog.result:
            urls_text = "\n".join(dialog.result)
            current_text = self.url_text.get("1.0", tk.END).strip()

            if current_text:
                full_text = current_text + "\n" + urls_text
            else:
                full_text = urls_text

            self.url_text.delete("1.0", tk.END)
            self.url_text.insert("1.0", full_text)
            messagebox.showinfo("Success", f"{len(dialog.result)} URLs were successfully generated and added.", parent=self.root)

    def create_widgets(self):
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
            text="Save in subfolder:",
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

        self.exit_red_hover = '#FF0000'
        self.exit_yellow_hover = '#FFD700'
        self.exit_white_text = '#FFFFFF'
        self.exit_dark_text_on_yellow = self.color_bg_color

        self.exit_btn.bind("<Enter>", self.on_exit_button_hover)
        self.exit_btn.bind("<Leave>", self.on_exit_button_leave)
        self.exit_btn.bind("<Button-1>", self.on_exit_button_click)

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(self.root, textvariable=self.status_var, style='TStatus.TLabel').pack(fill=tk.X, pady=(0,0), padx=5)

    def toggle_subfolder_entry(self):
        if self.use_subfolder_var.get() == 1:
            self.subfolder_entry.config(state=tk.NORMAL)
            self.confirm_subfolder_btn.config(state=tk.NORMAL)
        else:
            self.subfolder_entry.config(state=tk.DISABLED)
            self.confirm_subfolder_btn.config(state=tk.DISABLED)
            self.subfolder_var.set("")
            self.subfolder_entry.config(style='TEntry')

    def confirm_subfolder_selection(self):
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
        self.exit_btn.config(bg=self.exit_default_bg_color, fg=self.exit_default_fg_color,
                             activebackground=self.exit_default_active_bg, activeforeground=self.exit_default_active_fg)

    def on_exit_button_click(self, event):
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
        self.download_manager.custom_filenames = {}
        self.download_manager.batch_filename_prefix = None
        messagebox.showinfo("Reset", "Filenames reset to default (derived from URL).", parent=self.root)
        self.update_treeview_filenames()

    def update_treeview_filenames(self):
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

            if url in self.download_manager.custom_filenames:
                filename_to_display = self.download_manager.custom_filenames[url]
                assigned_filename_for_queue = filename_to_display
            elif self.download_manager.batch_filename_prefix:
                current_ext = self.download_manager.get_proper_extension(url, check_online=False)

                current_counter = extension_counters.get(current_ext, 0)
                current_counter += 1
                extension_counters[current_ext] = current_counter

                filename_to_display = f"{self.download_manager.batch_filename_prefix}_{current_counter:03d}{current_ext}"
                assigned_filename_for_queue = filename_to_display
            else:
                filename_to_display = self.download_manager.get_filename_from_url(url)
                ext = self.download_manager.get_proper_extension(url, check_online=False)
                if not filename_to_display.lower().endswith(ext) and '.' not in filename_to_display:
                    filename_to_display += ext
                assigned_filename_for_queue = filename_to_display

            self.tree.insert('', 'end', values=(filename_to_display, '', '0%', 'Ready'), iid=url)
            processed_urls_for_queue.append((url, assigned_filename_for_queue, final_save_path))

        with self.download_manager.download_queue.mutex:
            self.download_manager.download_queue.queue.clear()
        self.download_manager.add_to_queue(processed_urls_for_queue)

    def browse_path(self):
        path = filedialog.askdirectory(parent=self.root)
        if path:
            self.save_path_var.set(path)

    def add_urls(self):
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
        if self.download_manager.pause_flag:
            self.download_manager.resume_downloads()
            self.pause_btn.config(text="Pause / Resume")
            self.status_var.set("Downloading...")
        else:
            self.download_manager.pause_downloads()
            self.pause_btn.config(text="Resume")
            self.status_var.set("Paused")

    def stop_downloads(self):
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
        if not all([self.start_btn, self.pause_btn, self.stop_btn, self.add_btn, self.another_btn, self.exit_btn, self.tree, self.subfolder_checkbox, self.subfolder_entry, self.confirm_subfolder_btn]):
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
            
            error_text = f"Error: {info['error']}"

            if item_id in self.tree.get_children() and not self.tree.item(item_id, 'values')[3].startswith("Error"):
                self.tree.item(item_id, values=(
                    info['filename'],
                    "",
                    "0%",
                    error_text[:40]
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