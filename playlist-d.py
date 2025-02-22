import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sys
import shutil
import time

try:
    import yt_dlp
except ImportError:
    os.system(f"{sys.executable} -m pip install yt-dlp")
    import yt_dlp

# Check for ffmpeg in the system
ffmpeg_path = shutil.which("ffmpeg")
if not ffmpeg_path:
    messagebox.showwarning("FFmpeg Not Found", "FFmpeg is required but not found. Please install it manually from https://ffmpeg.org/download.html.")

def download_hook(d):
    # Global hook to update overall status (not used for individual videos)
    def update_gui():
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            percentage = (downloaded / total * 100) if total else 0
            progress_var.set(percentage)
            status_label.config(text=f"Downloading: {percentage:.1f}%")
        elif d['status'] == 'finished':
            progress_var.set(100)
            status_label.config(text="Download Complete!")
    root.after(0, update_gui)

def start_download():
    url = url_entry.get().strip()
    quality = quality_var.get()
    if not url:
        messagebox.showerror("Error", "Please enter a valid playlist URL!")
        return

    download_button.config(state="disabled")
    output_dir = output_path_var.get()
    if not output_dir:
        messagebox.showerror("Error", "Please select a download directory!")
        return
    os.makedirs(output_dir, exist_ok=True)

    format_map = {
        "Best Quality": "bestaudio+bv*",
        "1080p": "bv*[height<=1080]+ba",
        "720p": "bv*[height<=720]+ba",
        "480p": "bv*[height<=480]+ba",
        "360p": "bv*[height<=360]+ba",
        "Audio Only": "ba[ext=m4a]/ba"
    }
    selected_format = format_map.get(quality, "bestaudio+bv*")

    def download_thread():
        try:
            # Extract playlist information without downloading
            ydl_opts_extract = {'quiet': True, 'ignoreerrors': True}
            with yt_dlp.YoutubeDL(ydl_opts_extract) as ydl:
                info = ydl.extract_info(url, download=False)
            if info is None:
                messagebox.showerror("Error", "Could not extract playlist information.")
                return
            if 'entries' in info:
                entries = list(info['entries'])
            else:
                entries = [info]

            total_videos = len(entries)
            print(f"Total videos extracted: {total_videos}")

            # Clear previous video list if any
            for widget in videos_frame.winfo_children():
                widget.destroy()

            # Create a list of video items with individual progress bars
            progress_vars = []
            for i, entry in enumerate(entries, start=1):
                if entry is None:
                    continue
                video_title = entry.get("title", f"Video {i}")
                video_frame = ttk.Frame(videos_frame)
                video_frame.pack(fill="x", pady=2)
                title_label = ttk.Label(video_frame, text=video_title, width=40, anchor="w")
                title_label.pack(side="left", padx=(0, 5))
                p_var = tk.DoubleVar(value=0)
                video_progress = ttk.Progressbar(video_frame, variable=p_var, maximum=100)
                video_progress.pack(side="left", fill="x", expand=True)
                progress_vars.append(p_var)

            # Function to create an individual progress hook
            def make_progress_hook(p_var):
                def hook(d):
                    if d['status'] == 'downloading':
                        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                        downloaded = d.get('downloaded_bytes', 0)
                        percentage = (downloaded / total * 100) if total else 0
                        p_var.set(percentage)
                    elif d['status'] == 'finished':
                        p_var.set(100)
                return hook

            # Function to download a single video
            def download_single_video(entry, p_var, index):
                video_url = entry.get("webpage_url")
                if not video_url:
                    return
                video_opts = {
                    'outtmpl': os.path.join(output_dir, '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'),
                    'format': selected_format,
                    'progress_hooks': [make_progress_hook(p_var)],
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4'
                    }],
                    'ignoreerrors': True,
                    'quiet': True,
                }
                with yt_dlp.YoutubeDL(video_opts) as video_ydl:
                    video_ydl.download([video_url])
                print(f"Video {index} download complete.")

            # Create and start a thread for each video download
            video_threads = []
            for i, entry in enumerate(entries, start=1):
                if entry is None:
                    continue
                t = threading.Thread(target=download_single_video, args=(entry, progress_vars[i-1], i))
                video_threads.append(t)
                t.start()

            # Wait for all video threads to complete
            for t in video_threads:
                t.join()

            messagebox.showinfo("Success", "Playlist downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
        finally:
            download_button.config(state="normal")
            status_label.config(text="Ready to download")

    threading.Thread(target=download_thread, daemon=True).start()

def choose_directory():
    directory = filedialog.askdirectory()
    if directory:
        output_path_var.set(directory)

root = tk.Tk()
root.title("YouTube Playlist Downloader (By Haitomass)")
root.geometry("600x500")
root.minsize(400, 250)
root.maxsize(800, 600)

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

# Playlist URL
url_label = ttk.Label(frame, text="Playlist URL:")
url_label.pack(anchor="w")

url_entry = ttk.Entry(frame, width=50)
url_entry.pack(fill="x", pady=5)

# Quality selection
quality_label = ttk.Label(frame, text="Select Quality:")
quality_label.pack(anchor="w")

quality_var = tk.StringVar(value="Best Quality")
quality_options = ["Best Quality", "1080p", "720p", "480p", "360p", "Audio Only"]
quality_menu = ttk.Combobox(frame, textvariable=quality_var, values=quality_options, state="readonly")
quality_menu.pack(fill="x", pady=5)

# Download directory selection
output_path_var = tk.StringVar()
directory_frame = ttk.Frame(frame)
directory_frame.pack(fill="x", pady=5)
directory_label = ttk.Label(directory_frame, text="Download Directory:")
directory_label.pack(side="left")
directory_button = ttk.Button(directory_frame, text="Choose...", command=choose_directory)
directory_button.pack(side="left", padx=5)
directory_display = ttk.Label(directory_frame, textvariable=output_path_var)
directory_display.pack(side="left")

# Download button
download_button = ttk.Button(frame, text="Start Download", command=start_download)
download_button.pack(pady=10)

# Overall status label
status_label = ttk.Label(frame, text="Ready to download")
status_label.pack()

# Overall progress bar (optional, not linked to individual video progress)
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100)
progress_bar.pack(fill="x", pady=10)

# Frame for video list with individual progress bars
videos_frame = ttk.Frame(frame)
videos_frame.pack(fill="both", expand=True, pady=10)

root.mainloop()
