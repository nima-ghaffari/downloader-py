import os
import requests
import time
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, unquote
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
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
        
        button_text_color_ttk = '#FFFFFF'
        
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
                        foreground=button_text_color_ttk, 
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
        root.option_add('*Button*foreground', button_text_color_ttk)
        style.configure('Dialog.TButton', background=accent_color, foreground=button_text_color_ttk) 

class DownloadManager:
    def __init__(self):
        self.download_queue = Queue() 
        self.active_downloads = {}    
        self.completed_downloads = [] 
        self.failed_downloads = []    
        self.stop_flag = False        
        self.pause_flag = False       
        self.custom_filenames = {}    
        self.batch_filename = None    
        self.file_counter = 1         
        self.executor = ThreadPoolExecutor(max_workers=5) 

    def set_custom_filename(self, url, filename):
        self.custom_filenames[url] = filename

    def set_batch_filename(self, filename):
        self.batch_filename = filename
        self.file_counter = 1  

    def add_to_queue(self, urls, save_path):
        for url in urls:
            self.download_queue.put((url, save_path))

    def get_sequential_filename(self, url):
        ext = self.get_proper_extension(url)
        if self.batch_filename:
            filename = f"{self.batch_filename}_{self.file_counter:03d}{ext}" 
            self.file_counter += 1
            return filename
        else:
            return self.get_filename_from_url(url)

    def get_proper_extension(self, url):
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
        if 'srt' in url_lower and not 'srt.' in url_lower: return '.srt'
        if 'sub' in url_lower and not 'sub.' in url_lower: return '.sub'
        if 'vtt' in url_lower and not 'vtt.' in url_lower: return '.vtt'
        if 'mp3' in url_lower and not 'mp3.' in url_lower: return '.mp3'
        if 'pdf' in url_lower and not 'pdf.' in url_lower: return '.pdf'
        if 'zip' in url_lower and not 'zip.' in url_lower: return '.zip'
        if 'jpg' in url_lower or 'jpeg' in url_lower: return '.jpg'
        if 'png' in url_lower and not 'png.' in url_lower: return '.png'
        if 'gif' in url_lower and not 'gif.' in url_lower: return '.gif'

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

    def download_file(self, url, save_path):
        filename = "" 
        filepath = "" 
        try:
            if url in self.custom_filenames:
                filename = self.custom_filenames[url]
            else:
                base_filename_from_url = self.get_filename_from_url(url)
                ext = self.get_proper_extension(url)
                
                if not base_filename_from_url.lower().endswith(ext) and '.' not in base_filename_from_url:
                    base_filename_from_url += ext
                filename = base_filename_from_url
                
            if self.batch_filename and not url in self.custom_filenames:
                filename = self.get_sequential_filename(url)
                
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
            error_info = {
                'status': 'failed', 'filename': filename, 'url': url, 'error': str(e)
            }
            self.failed_downloads.append(error_info)
            self.active_downloads.pop(url, None)
            if os.path.exists(filepath): 
                os.remove(filepath)
            return error_info

    def start_downloads(self):
        self.stop_flag = False
        self.pause_flag = False
        futures = []
        while not self.download_queue.empty() and not self.stop_flag:
            url, save_path = self.download_queue.get()
            futures.append(self.executor.submit(self.download_file, url, save_path))
        
        pass 

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
            self.default_font = Font(family="Segoe UI", size=9)
            self.heading_font = Font(family="Segoe UI", size=10, weight="bold")
            self.large_heading_font = Font(family="Segoe UI", size=12, weight="bold")
            self.button_font = Font(family="Berlin Sans Demi", size=10, weight="bold") 
        except:
            self.default_font = Font(family="Tahoma", size=9)
            self.heading_font = Font(family="Tahoma", size=10, weight="bold")
            self.large_heading_font = Font(family="Tahoma", size=12, weight="bold")
            self.button_font = Font(family="Segoe UI Semibold", size=10, weight="bold") 

        self.fonts_dict = {
            'default': self.default_font,
            'heading': self.heading_font,
            'large_heading': self.large_heading_font,
            'button': self.button_font 
        }

        try:
            CustomTheme.apply(root, self.fonts_dict)
        except Exception as e:
            print(f"Error applying theme: {e}") 
        
        self.download_manager = DownloadManager()
        self.create_widgets() 
        
        self.update_interval = 500 
        self.root.after(self.update_interval, self.update_download_status)

    def create_widgets(self):
        """Creates all the UI elements (frames, labels, entries, buttons, treeview)."""

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

        self.another_btn = ttk.Button(left_control_buttons_frame, text="Another", command=self.clear_all_content, width=fixed_button_width) 
        self.another_btn.pack(side=tk.LEFT, padx=(0,1)) 

        right_control_buttons_frame = ttk.Frame(self.root, style='TFrame', padding=(2, 2)) 
        right_control_buttons_frame.pack(side=tk.RIGHT, anchor=tk.SE, padx=5, pady=(2, 5)) 

        style_obj = ttk.Style()
        default_button_bg = style_obj.lookup('TButton', 'background')
        default_button_fg = style_obj.lookup('TButton', 'foreground') 
        default_button_active_bg = style_obj.lookup('TButton', 'background', ['active'])
        default_button_active_fg = style_obj.lookup('TButton', 'foreground', ['active']) 

        self.exit_btn = tk.Button(right_control_buttons_frame, text="Exit", 
                                   font=self.fonts_dict['button'], 
                                   width=fixed_button_width, 
                                   bg=default_button_bg, 
                                   fg=default_button_fg, 
                                   relief=tk.FLAT, borderwidth=0, padx=10, pady=5,
                                   activebackground=default_button_active_bg, 
                                   activeforeground=default_button_active_fg) 
        self.exit_btn.pack(side=tk.RIGHT)
        
        self.exit_default_bg_color = default_button_bg
        self.exit_default_fg_color = default_button_fg
        self.exit_default_active_bg = default_button_active_bg
        self.exit_default_active_fg = default_button_active_fg
        
        self.exit_red_hover = '#FF0000' 
        self.exit_yellow_hover = '#FFD700' 
        self.exit_white_text = '#FFFFFF' 
        self.exit_dark_text_on_yellow = style_obj.lookup('TFrame', 'background') 

        self.exit_btn.bind("<Enter>", self.on_exit_button_hover)
        self.exit_btn.bind("<Leave>", self.on_exit_button_leave)
        self.exit_btn.bind("<Button-1>", self.on_exit_button_click) 

        self.status_var = tk.StringVar()
        self.status_var.set("Ready") 
        ttk.Label(self.root, textvariable=self.status_var, style='TStatus.TLabel').pack(fill=tk.X, pady=(0,0), padx=5) 

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
                self.download_manager.download_queue = Queue() 
                self.root.quit()
        else:
            self.root.quit()

    def set_filenames(self):
        choice = messagebox.askquestion("Filename Options", 
                                        "Do you want to set names for all files as a batch or individually?",
                                        detail="Click 'Yes' for batch naming, 'No' for individual names.",
                                        icon='question', parent=self.root)
        
        if choice == 'yes':
            base_name = simpledialog.askstring("Batch Naming", 
                                              "Enter base filename (numbers will be added automatically, e.g., 'My_File_001'):",
                                              parent=self.root)
            if base_name:
                self.download_manager.set_batch_filename(base_name)
                self.update_treeview_filenames() 
        else:
            self.edit_filenames()

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

            new_name = simpledialog.askstring(
                "Edit Filename",
                f"New name for:\n{url}",
                initialvalue=default_name,
                parent=self.root
            )
            if new_name:
                if '.' not in new_name: 
                    new_name += self.download_manager.get_proper_extension(url)
                self.download_manager.set_custom_filename(url, new_name)
        
        self.update_treeview_filenames() 

    def reset_filenames(self):
        self.download_manager.custom_filenames = {}
        self.download_manager.batch_filename = None
        self.download_manager.file_counter = 1
        messagebox.showinfo("Reset", "Filenames reset to default (derived from URL).", parent=self.root)
        self.update_treeview_filenames() 

    def update_treeview_filenames(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        urls_text = self.url_text.get("1.0", tk.END).strip()
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]

        temp_file_counter = 1 

        for url in urls:
            filename_to_display = ""
            if url in self.download_manager.custom_filenames:
                filename_to_display = self.download_manager.custom_filenames[url]
            elif self.download_manager.batch_filename:
                ext = self.download_manager.get_proper_extension(url)
                filename_to_display = f"{self.download_manager.batch_filename}_{temp_file_counter:03d}{ext}"
                temp_file_counter += 1
            else:
                filename_to_display = self.download_manager.get_filename_from_url(url)
                ext = self.download_manager.get_proper_extension(url)
                if not filename_to_display.lower().endswith(ext) and '.' not in filename_to_display:
                    filename_to_display += ext
                    
            self.tree.insert('', 'end', values=(filename_to_display, '', '0%', 'Ready')) 

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
        save_path = self.save_path_var.get()
        
        if not os.path.exists(save_path):
            try:
                os.makedirs(save_path)
            except OSError as e:
                messagebox.showerror("Error", f"Could not create save directory: {e}", parent=self.root)
                return
        
        for item in list(self.tree.get_children()): 
            self.tree.delete(item)

        self.download_manager.add_to_queue(urls, save_path)
        
        self.update_treeview_filenames()
        
        self.url_text.delete("1.0", tk.END) 
        self.status_var.set(f"Added {len(urls)} URLs to queue.") 

    def start_downloads(self):
        if self.download_manager.download_queue.empty() and not self.download_manager.active_downloads:
            messagebox.showwarning("Warning", "No files in queue or active downloads to start.", parent=self.root)
            return
            
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL, text="Pause / Resume") 
        self.stop_btn.config(state=tk.NORMAL)
        self.add_btn.config(state=tk.DISABLED) 
        self.another_btn.config(state=tk.DISABLED) 
        if self.download_manager.active_downloads or not self.download_manager.download_queue.empty():
            self.exit_btn.config(state=tk.DISABLED) 
        
        if self.download_manager.batch_filename:
            self.download_manager.file_counter = 1

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


    def update_download_status(self):
        if not all([self.start_btn, self.pause_btn, self.stop_btn, self.add_btn, self.another_btn, self.exit_btn, self.tree]):
            self.root.after(self.update_interval, self.update_download_status)
            return

        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, 'values')
            current_filename_display = values[0] if values else ""

            matched_url = None
            for url, info in self.download_manager.active_downloads.items():
                if current_filename_display == info['filename']:
                    matched_url = url
                    break
            
            if matched_url:
                info = self.download_manager.active_downloads[matched_url]
                
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
            
            for item_id in self.tree.get_children():
                values = self.tree.item(item_id, 'values')
                if values and values[0] == info['filename'] and values[3] != "Completed": 
                    self.tree.item(item_id, values=(
                        info['filename'],
                        completed_size_display, 
                        "100%",
                        "Completed" 
                    ))
                    break
                
        while self.download_manager.failed_downloads:
            info = self.download_manager.failed_downloads.pop(0)
            for item_id in self.tree.get_children():
                values = self.tree.item(item_id, 'values')
                if values and values[0] == info['filename'] and not values[3].startswith("Error"): 
                    self.tree.item(item_id, values=(
                        info['filename'],
                        "", 
                        "0%",
                        f"Error: {info['error'][:30]}..." 
                    ))
                    break
        
        if not self.download_manager.active_downloads and self.download_manager.download_queue.empty():
            if self.status_var.get() not in ["Ready", "All downloads finished.", "Stopping downloads.", "Ready for new downloads."]:
                self.status_var.set("All downloads finished.") 
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED, text="Pause / Resume")
            self.stop_btn.config(state=tk.DISABLED)
            self.add_btn.config(state=tk.NORMAL)
            self.another_btn.config(state=tk.NORMAL) 
            self.exit_btn.config(state=tk.NORMAL) 
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