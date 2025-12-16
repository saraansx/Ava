import tkinter as tk
from tkinter import scrolledtext
import threading
import time

class AvaGUI:
    def __init__(self, app_instance):
        self.app = app_instance
        self.root = tk.Tk()
        self.root.title("Ava AI")
        self.root.geometry("800x600")
        self.root.configure(bg="#000000")
        
        # Make the window frameless
        self.root.overrideredirect(True)
        
        # Transparency (alpha)
        try:
            self.root.attributes("-alpha", 0.95)
        except:
            pass

        # Fonts & Colors (Terminal Style)
        self.font_main = ("Consolas", 12)
        self.font_header = ("Consolas", 11, "bold")
        self.font_logs = ("Consolas", 9)
        
        self.bg_color = "#000000"
        self.fg_color = "#E0E0E0"
        
        self.accent_user = "#00FF7F" # Spring Green
        self.accent_ava = "#00BFFF"  # Deep Sky Blue
        self.dim_color = "#666666"

        self._setup_ui()
        
        # Dragging logic (since frameless)
        self._drag_data = {"x": 0, "y": 0}
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def stop_move(self, event):
        self._drag_data["x"] = None
        self._drag_data["y"] = None

    def do_move(self, event):
        deltax = event.x - self._drag_data["x"]
        deltay = event.y - self._drag_data["y"]
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def _setup_ui(self):
        # Custom Title Bar / Header
        title_bar = tk.Frame(self.root, bg="#111111", relief="flat", bd=0, height=25)
        title_bar.pack(fill="x", side="top", pady=0)
        title_bar.pack_propagate(False) # Force height

        tk.Label(title_bar, text=" AVA TERMINAL ", fg=self.accent_ava, bg="#111111", font=("Consolas", 10, "bold")).pack(side="left", padx=5)
        
        btn_close = tk.Button(title_bar, text="[X]", command=self.on_close, bg="#111111", fg="#FF4444", bd=0, activebackground="#330000", activeforeground="white", font=("Consolas", 10, "bold"), cursor="hand2")
        btn_close.pack(side="right", padx=5)

        # Main Log Container (The only element now)
        main_container = tk.Frame(self.root, bg="black", padx=10, pady=10)
        main_container.pack(fill="both", expand=True)

        self.txt_logs = scrolledtext.ScrolledText(main_container, font=self.font_main, bg="black", fg="#CCCCCC", insertbackground="white", relief="flat", padx=10, pady=10)
        self.txt_logs.pack(fill="both", expand=True)
        
        # Tags for log coloring
        self.txt_logs.tag_config("user_header", foreground=self.accent_user, font=("Consolas", 12, "bold"))
        self.txt_logs.tag_config("user_text", foreground="white")
        
        self.txt_logs.tag_config("ava_header", foreground=self.accent_ava, font=("Consolas", 12, "bold"))
        self.txt_logs.tag_config("ava_text", foreground="#DDDDDD")
        
        self.txt_logs.tag_config("system_header", foreground=self.dim_color, font=("Consolas", 10, "bold"))
        self.txt_logs.tag_config("info", foreground="#888888", font=self.font_logs)
        self.txt_logs.tag_config("tool", foreground="#FFA500", font=self.font_logs) 
        self.txt_logs.tag_config("model", foreground="#4682B4", font=self.font_logs)
        self.txt_logs.tag_config("error", foreground="#FF4444", font=self.font_logs) 

    def update_user_text(self, text):
        # Print to main log instead of separate label
        self.txt_logs.insert(tk.END, "\n> USER\n", "user_header")
        self.txt_logs.insert(tk.END, f"{text}\n", "user_text")
        self.txt_logs.see(tk.END)
        self.root.update_idletasks()

    def update_ava_text(self, text):
        # Print to main log instead of separate label
        self.txt_logs.insert(tk.END, "\n> AVA\n", "ava_header")
        self.txt_logs.insert(tk.END, f"{text}\n", "ava_text")
        self.txt_logs.see(tk.END)
        self.root.update_idletasks()

    def add_log(self, message, tag="info"):
        # self.txt_logs.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] ", "system_header")
        self.txt_logs.insert(tk.END, f">> {message}\n", tag)
        self.txt_logs.see(tk.END)

    def start(self):
        thread = threading.Thread(target=self.app.start_background_loop, args=(self,), daemon=True)
        thread.start()
        self.root.mainloop()

    def on_close(self):
        self.root.destroy()
        import os
        os._exit(0)
