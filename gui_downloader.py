import tkinter as tk
from tkinter import ttk, filedialog
import requests
import threading
import os
import shutil
from tqdm import tqdm
from ttkthemes import ThemedStyle

class Downloader:
    def __init__(self):
        self.saveto = ""
        self.cancel_download = False
        self.window = tk.Tk()
        self.window.title("Python GUI Downloader")
        self.window.geometry('400x350')

        style = ThemedStyle(self.window)
        style.set_theme("plastik")

        self.url_label = ttk.Label(self.window, text='Enter URL')
        self.url_label.pack(pady=10)

        self.url_entry = ttk.Entry(self.window, width=40)
        self.url_entry.pack(pady=5)

        self.browse_button = ttk.Button(self.window, text='Browse', command=self.browse_file)
        self.browse_button.pack(pady=5)

        self.download_button = ttk.Button(self.window, text='Download', command=self.download)
        self.download_button.pack(pady=10)

        self.cancel_button = ttk.Button(self.window, text='Cancel Download', command=self.cancel_download_action, state=tk.DISABLED)
        self.cancel_button.pack(pady=5)

        self.progress_bar = ttk.Progressbar(self.window, orient='horizontal', length=300, mode='determinate')
        self.progress_bar.pack(pady=10)

        self.progress_text = tk.StringVar()
        self.progress_label = ttk.Label(self.window, textvariable=self.progress_text)
        self.progress_label.pack()

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.mainloop()

    def browse_file(self):
        saveto = filedialog.asksaveasfilename(initialfile=self.url_entry.get().split('/')[-1].split('?')[0])
        if saveto:
            self.saveto = saveto

    def download(self):
        url = self.url_entry.get()
        if not url:
            return

        if not self.saveto:
            self.progress_text.set("Error: Select a valid save location")
            return

        self.download_button.configure(state=tk.DISABLED)
        self.cancel_button.configure(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        self.progress_text.set("Downloading...")
        self.cancel_download = False

        threading.Thread(target=self.start_download, args=(url,)).start()

    def start_download(self, url):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size_in_bytes = int(response.headers.get("content-length", 0))
            block_size = 1024 * 1024  # 1MB

            self.progress_bar['maximum'] = total_size_in_bytes
            self.progress_bar['value'] = 0

            downloaded_size = 0

            with open(self.saveto + '.crdownload', 'wb') as f, tqdm.wrapattr(f, "write", unit="B", unit_scale=True, unit_divisor=1024, miniters=1, total=total_size_in_bytes) as f_tqdm:
                for data in response.iter_content(block_size):
                    if self.cancel_download:
                        break

                    f_tqdm.write(data)
                    downloaded_size += len(data)
                    self.progress_bar['value'] = downloaded_size

                    progress_percent = int((downloaded_size / total_size_in_bytes) * 100)
                    self.progress_text.set(f"Downloading... {progress_percent}%")
                    self.window.update()

                if not self.cancel_download:
                    self.progress_text.set("Download Complete")
                    f.close()  # Close the file object before renaming
                    shutil.move(self.saveto + ".crdownload", self.saveto)  # Remove .crdownload extension
                else:
                    self.progress_text.set("Download Canceled")
                    os.remove(self.saveto + ".crdownload")  # Remove .crdownload file

        except requests.exceptions.RequestException:
            self.progress_text.set("Error: Failed to download")

        finally:
            self.download_button.configure(state=tk.NORMAL)
            self.cancel_button.configure(state=tk.DISABLED)

    def cancel_download_action(self):
        self.cancel_download = True

    def on_close(self):
        if self.cancel_button['state'] == tk.NORMAL:
            self.cancel_download_action()

        self.window.destroy()

Downloader()
