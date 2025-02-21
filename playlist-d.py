import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import sys
import shutil

try:
    import yt_dlp
except ImportError:
    os.system(f"{sys.executable} -m pip install yt-dlp")
    import yt_dlp

# البحث عن ffmpeg في النظام
ffmpeg_path = shutil.which("ffmpeg")
if not ffmpeg_path:
    messagebox.showwarning("FFmpeg Not Found", "FFmpeg is required but not found. Please install it manually from https://ffmpeg.org/download.html.")

def download_hook(d):
    def update_gui():
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            percentage = (downloaded / total * 100) if total else 0
            progress_var.set(percentage)
            status_label.config(text=f"\U0001F4E5 Downloading: {percentage:.1f}%")
        elif d['status'] == 'finished':
            progress_var.set(100)
            status_label.config(text="✅ Download Complete!")
    root.after(0, update_gui)

def start_download():
    url = url_entry.get().strip()
    quality = quality_var.get()
    if not url:
        messagebox.showerror("Error", "Please enter a valid playlist URL!")
        return

    download_button.config(state="disabled")
    output_dir = "downloads"
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
            # استخراج معلومات القائمة دون تحميل
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
            print(f"Total videos extracted: {total_videos}")  # للتأكد من العدد المستخرج
            for i, entry in enumerate(entries, start=1):
                if entry is None:
                    continue
                status_label.config(text=f"Downloading video {i}/{total_videos}")
                video_url = entry.get("webpage_url")
                if not video_url:
                    continue
                video_opts = {
                    'outtmpl': os.path.join(output_dir, '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'),
                    'format': selected_format,
                    'progress_hooks': [download_hook],
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4'
                    }],
                    'ignoreerrors': True,
                }
                with yt_dlp.YoutubeDL(video_opts) as video_ydl:
                    video_ydl.download([video_url])
            messagebox.showinfo("Success", "🎉 Playlist downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"❌ An error occurred:\n{e}")
        finally:
            download_button.config(state="normal")
            progress_var.set(0)
            status_label.config(text="✅ Ready to download")

    threading.Thread(target=download_thread, daemon=True).start()

root = tk.Tk()
root.title("🎥 YouTube Playlist Downloader (With Audio)")
root.geometry("500x300")
root.minsize(400, 250)
root.maxsize(700, 450)

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

url_label = ttk.Label(frame, text="📌 Playlist URL:")
url_label.pack(anchor="w")

url_entry = ttk.Entry(frame, width=50)
url_entry.pack(fill="x", pady=5)

quality_label = ttk.Label(frame, text="🎚 Select Quality:")
quality_label.pack(anchor="w")

quality_var = tk.StringVar(value="Best Quality")
quality_options = ["Best Quality", "1080p", "720p", "480p", "360p", "Audio Only"]
quality_menu = ttk.Combobox(frame, textvariable=quality_var, values=quality_options, state="readonly")
quality_menu.pack(fill="x", pady=5)

download_button = ttk.Button(frame, text="🚀 Start Download", command=start_download)
download_button.pack(pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100)
progress_bar.pack(fill="x", pady=10)

status_label = ttk.Label(frame, text="✅ Ready to download")
status_label.pack()

root.mainloop()
