import tkinter as tk
from tkinter import filedialog, messagebox
from crawler import process_multi_chapter
import asyncio
import time


def start_crawling():
    manga_url = url_entry.get()
    path = path_entry.get()
    if not path.endswith("/"):
        path += "/"
    try:
        start_chap = int(start_chapter_entry.get())
        end_chap = int(end_chapter_entry.get())
    except:
        messagebox.showerror("Input Error", "Please enter number.")
        return

    if not manga_url or not path or start_chap <= 0 or end_chap < start_chap:
        messagebox.showerror("Input Error", "Please provide valid inputs.")
        return

    start = time.time()
    # Run the crawler asynchronously
    asyncio.run(process_multi_chapter(manga_url, start_chap, end_chap, path))
    end = time.time()
    messagebox.showinfo(
        "Success", f"Crawling completed successfully.\nCrawling time: {end-start}"
    )


def browse_directory():
    folder_selected = filedialog.askdirectory()
    path_entry.delete(0, tk.END)
    path_entry.insert(0, folder_selected)


# Create main window
root = tk.Tk()
root.title("Manga4Life Crawler")

# Create and place widgets
tk.Label(root, text="Manga URL:").grid(row=0, column=0, padx=10, pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Path:").grid(row=1, column=0, padx=10, pady=5)
path_entry = tk.Entry(root, width=50)
path_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=browse_directory).grid(
    row=1, column=2, padx=10, pady=5
)

tk.Label(root, text="Start Chapter:").grid(row=2, column=0, padx=10, pady=5)
start_chapter_entry = tk.Entry(root, width=10)
start_chapter_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="End Chapter:").grid(row=3, column=0, padx=10, pady=5)
end_chapter_entry = tk.Entry(root, width=10)
end_chapter_entry.grid(row=3, column=1, padx=10, pady=5)

tk.Button(root, text="Start Crawling", command=start_crawling).grid(
    row=4, column=1, padx=10, pady=20
)

# Start the Tkinter event loop
root.mainloop()
