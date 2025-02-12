import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import yt_dlp

# دالة الاستدعاء عند التنزيل
def download_hook(d):
    def update_gui():
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            percentage = (downloaded / total * 100) if total else 0
            progress_var.set(percentage)
            status_label.config(text=f"📥 تحميل: {percentage:.1f}%")
        elif d['status'] == 'finished':
            progress_var.set(100)
            status_label.config(text="✅ تم التحميل بنجاح!")

    root.after(0, update_gui)

# بدء التنزيل
def start_download():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("خطأ", "يرجى إدخال رابط البلايليست!")
        return

    download_button.config(state="disabled")

    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)

    def download_thread():
        try:
            ydl_opts = {
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'format': 'best[ext=mp4]/best[ext=webm]/best',
                'noplaylist': False,  # تأكد من تحميل قائمة التشغيل كاملة
                'progress_hooks': [download_hook],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("نجاح", "🎉 تم تنزيل البلايليست بنجاح!")
        except Exception as e:
            messagebox.showerror("خطأ", f"❌ حدث خطأ أثناء التنزيل:\n{e}")
        finally:
            download_button.config(state="normal")
            progress_var.set(0)
            status_label.config(text="✅ جاهز للتنزيل")

    threading.Thread(target=download_thread, daemon=True).start()

# واجهة المستخدم
root = tk.Tk()
root.title("🔻 تحميل قائمة تشغيل يوتيوب 🔻")

frame = ttk.Frame(root, padding=20)
frame.pack()

url_label = ttk.Label(frame, text="📌 رابط البلايليست:")
url_label.grid(row=0, column=0, sticky="w")

url_entry = ttk.Entry(frame, width=50)
url_entry.grid(row=1, column=0, pady=10)

download_button = ttk.Button(frame, text="🚀 بدء التحميل", command=start_download)
download_button.grid(row=2, column=0, pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100)
progress_bar.grid(row=3, column=0, pady=10, sticky="ew")

status_label = ttk.Label(frame, text="✅ جاهز للتنزيل")
status_label.grid(row=4, column=0)

root.mainloop()
