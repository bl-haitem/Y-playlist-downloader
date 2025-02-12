import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import sys

# تثبيت yt-dlp تلقائيًا إن لم يكن موجودًا
try:
    import yt_dlp
except ImportError:
    os.system(f"{sys.executable} -m pip install yt-dlp")
    import yt_dlp

# تحديث التقدم أثناء التنزيل
def download_hook(d):
    def update_gui():
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            percentage = (downloaded / total * 100) if total else 0
            progress_var.set(percentage)
            status_label.config(text=f"📥 Downloading: {percentage:.1f}%")
        elif d['status'] == 'finished':
            progress_var.set(100)
            status_label.config(text="✅ Download Complete!")

    root.after(0, update_gui)

# دالة بدء التحميل
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
        "Best Quality": "best",
        "1080p": "bv*[height<=1080][ext=mp4]",
        "720p": "bv*[height<=720][ext=mp4]",
        "480p": "bv*[height<=480][ext=mp4]",
        "360p": "bv*[height<=360][ext=mp4]",
        "Audio Only": "ba[ext=m4a]/ba"
    }

    selected_format = format_map.get(quality, "best")

    def download_thread():
        try:
            ydl_opts = {
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'format': selected_format,  # اختيار الصيغة المناسبة بدون ffmpeg
                'noplaylist': False,
                'progress_hooks': [download_hook],
                'postprocessors': [],  # إزالة `ffmpeg` من العمليات النهائية
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Success", "🎉 Playlist downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"❌ An error occurred:\n{e}")
        finally:
            download_button.config(state="normal")
            progress_var.set(0)
            status_label.config(text="✅ Ready to download")

    threading.Thread(target=download_thread, daemon=True).start()

# تصميم الواجهة
root = tk.Tk()
root.title("🎥 YouTube Playlist Downloader (No FFmpeg)")

# ضبط حجم النافذة لتكون مرنة
root.geometry("500x300")
root.minsize(400, 250)
root.maxsize(700, 450)

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

url_label = ttk.Label(frame, text="📌 Playlist URL:")
url_label.pack(anchor="w")

url_entry = ttk.Entry(frame, width=50)
url_entry.pack(fill="x", pady=5)

# قائمة لاختيار الجودة
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
