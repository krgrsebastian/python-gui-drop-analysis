import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np

class VideoAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Analysis Tool")
        
        self.selected_videos = []
        self.queue = []
        
        self.crop_coords = None
        self.rotation_angle = 0
        self.baseline_coords = None
        self.baseline_y = 0
        
        self.setup_gui()

    def setup_gui(self):
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("TLabel", padding=6)
        style.configure("TEntry", padding=6)
        
        # Videoauswahl
        self.video_label = ttk.Label(self.root, text="Select Video:")
        self.video_label.grid(row=0, column=0, padx=10, pady=10)
        self.video_button = ttk.Button(self.root, text="Browse", command=self.select_video)
        self.video_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Zielpfadauswahl
        self.target_label = ttk.Label(self.root, text="Select Target Path:")
        self.target_label.grid(row=1, column=0, padx=10, pady=10)
        self.target_button = ttk.Button(self.root, text="Browse", command=self.select_target_path)
        self.target_button.grid(row=1, column=1, padx=10, pady=10)
        
        # Bildauswahl und Cropping
        self.crop_label = ttk.Label(self.root, text="Crop Image:")
        self.crop_label.grid(row=2, column=0, padx=10, pady=10)
        self.crop_button = ttk.Button(self.root, text="Select Image from Video", command=self.select_image_from_video)
        self.crop_button.grid(row=2, column=1, padx=10, pady=10)
        
        # Bildrotation
        self.rotate_label = ttk.Label(self.root, text="Rotate Image (degrees):")
        self.rotate_label.grid(row=3, column=0, padx=10, pady=10)
        self.rotate_entry = ttk.Entry(self.root)
        self.rotate_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # Baseline-Auswahl
        self.baseline_label = ttk.Label(self.root, text="Select Baseline:")
        self.baseline_label.grid(row=4, column=0, padx=10, pady=10)
        self.baseline_slider = tk.Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, length=300, command=self.set_baseline)
        self.baseline_slider.grid(row=4, column=1, padx=10, pady=10)
        
        # Threshold-Einstellungen
        self.threshold1_label = ttk.Label(self.root, text="Threshold 1:")
        self.threshold1_label.grid(row=5, column=0, padx=10, pady=10)
        self.threshold1_slider = tk.Scale(self.root, from_=0, to=255, orient=tk.HORIZONTAL, length=300)
        self.threshold1_slider.grid(row=5, column=1, padx=10, pady=10)
        
        self.threshold2_label = ttk.Label(self.root, text="Threshold 2:")
        self.threshold2_label.grid(row=6, column=0, padx=10, pady=10)
        self.threshold2_slider = tk.Scale(self.root, from_=0, to=255, orient=tk.HORIZONTAL, length=300)
        self.threshold2_slider.grid(row=6, column=1, padx=10, pady=10)
        
        # Parameteranzeige
        self.param_label = ttk.Label(self.root, text="Parameters:")
        self.param_label.grid(row=7, column=0, padx=10, pady=10)
        
        self.param_display = ttk.Label(self.root, text="")
        self.param_display.grid(row=7, column=1, padx=10, pady=10)
        
        # Warteschlange und Analyse starten
        self.queue_button = ttk.Button(self.root, text="Add to Queue", command=self.add_to_queue)
        self.queue_button.grid(row=8, column=0, padx=10, pady=10)
        
        self.start_button = ttk.Button(self.root, text="Start Analysis", command=self.start_analysis)
        self.start_button.grid(row=8, column=1, padx=10, pady=10)

    def select_video(self):
        video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
        if video_path:
            self.selected_videos.append(video_path)
            # messagebox.showinfo("Selected Video", f"Selected: {video_path}")
    
    def select_target_path(self):
        target_path = filedialog.askdirectory()
        if target_path:
            self.target_path = target_path
            # messagebox.showinfo("Selected Target Path", f"Selected: {target_path}")
    
    def select_image_from_video(self):
        if not self.selected_videos:
            messagebox.showwarning("Warning", "Please select a video first.")
            return
        
        video_path = self.selected_videos[-1]
        self.cap = cv2.VideoCapture(video_path)
        
        self.video_window = tk.Toplevel(self.root)
        self.video_window.title("Select Frame")
        
        self.video_label = ttk.Label(self.video_window)
        self.video_label.pack()
        
        self.pause = False
        
        self.timeline = tk.Scale(self.video_window, from_=0, to=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))-1, orient=tk.HORIZONTAL, length=400, command=self.set_frame)
        self.timeline.pack()
        
        controls_frame = ttk.Frame(self.video_window)
        controls_frame.pack()
        
        self.play_button = ttk.Button(controls_frame, text="Play/Pause", command=self.toggle_pause)
        self.play_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.prev_frame_button = ttk.Button(controls_frame, text="<<", command=self.prev_frame)
        self.prev_frame_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.next_frame_button = ttk.Button(controls_frame, text=">>", command=self.next_frame)
        self.next_frame_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.current_frame_pos = 0
        self.show_frame()

        self.video_window.bind("<space>", self.toggle_pause)
        self.video_window.protocol("WM_DELETE_WINDOW", self.on_video_window_close)
        
        self.select_frame_button = ttk.Button(self.video_window, text="Select Frame", command=self.capture_frame)
        self.select_frame_button.pack()

    def show_frame(self):
        if not self.pause:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_pos)
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                self.display_frame(frame)
                self.current_frame_pos += 1
                self.timeline.set(self.current_frame_pos)
                if self.current_frame_pos >= int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)):
                    self.current_frame_pos = 0  # Loop the video
            self.video_label.after(30, self.show_frame)
    
    def display_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

    def set_frame(self, pos):
        self.current_frame_pos = int(pos)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_pos)
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            self.display_frame(frame)
    
    def toggle_pause(self, event=None):
        self.pause = not self.pause
        if not self.pause:
            self.show_frame()
    
    def prev_frame(self):
        self.current_frame_pos = max(0, self.current_frame_pos - 1)
        self.set_frame(self.current_frame_pos)
    
    def next_frame(self):
        self.current_frame_pos = min(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1, self.current_frame_pos + 1)
        self.set_frame(self.current_frame_pos)
    
    def on_video_window_close(self):
        self.cap.release()
        self.video_window.destroy()
    
    def capture_frame(self):
        self.pause = True
        self.cap.release()
        self.video_window.destroy()
        self.show_frame_for_cropping(self.current_frame)
    
    def show_frame_for_cropping(self, frame):
        self.original_image = Image.fromarray(frame)
        self.rotated_image = self.original_image
        self.crop_window = tk.Toplevel(self.root)
        self.crop_window.title("Crop Image")
        
        self.canvas_crop = tk.Canvas(self.crop_window, width=self.rotated_image.width, height=self.rotated_image.height)
        self.canvas_crop.pack()
        
        self.rotate_label = ttk.Label(self.crop_window, text="Rotate Image (degrees):")
        self.rotate_label.pack(pady=5)
        
        self.rotate_entry_crop = ttk.Entry(self.crop_window)
        self.rotate_entry_crop.pack(pady=5)
        self.rotate_entry_crop.bind("<Return>", self.rotate_image_entry_crop)
        
        self.show_rotated_image()

        self.canvas_crop.bind("<Button-1>", self.start_crop)
        self.canvas_crop.bind("<B1-Motion>", self.do_crop)
        self.canvas_crop.bind("<ButtonRelease-1>", self.end_crop)
        
        self.crop_rectangle = None
        self.crop_start_x = None
        self.crop_start_y = None
        
        self.save_button_in_crop = ttk.Button(self.crop_window, text="Save and Continue", command=self.save_cropped_image)
        self.save_button_in_crop.pack()

    def rotate_image_entry_crop(self, event):
        if hasattr(self, 'original_image'):
            try:
                angle = int(self.rotate_entry_crop.get())
                self.rotation_angle = angle
                self.rotated_image = self.original_image.rotate(self.rotation_angle, expand=True)
                self.show_rotated_image()
                self.update_parameters()
            except ValueError:
                messagebox.showwarning("Warning", "Please enter a valid integer.")
        else:
            messagebox.showwarning("Warning", "Please select an image first.")

    def show_rotated_image(self):
        self.tk_image = ImageTk.PhotoImage(self.rotated_image)
        self.canvas_crop.config(width=self.rotated_image.width, height=self.rotated_image.height)
        self.canvas_crop.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas_crop.image = self.tk_image  # To prevent garbage collection

    def start_crop(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        if self.crop_rectangle:
            self.canvas_crop.delete(self.crop_rectangle)
        self.crop_rectangle = self.canvas_crop.create_rectangle(self.crop_start_x, self.crop_start_y, self.crop_start_x, self.crop_start_y, outline='red')

    def do_crop(self, event):
        self.canvas_crop.coords(self.crop_rectangle, self.crop_start_x, self.crop_start_y, event.x, event.y)

    def end_crop(self, event):
        self.crop_end_x = event.x
        self.crop_end_y = event.y
        self.cropped_image = self.rotated_image.crop((self.crop_start_x, self.crop_start_y, self.crop_end_x, self.crop_end_y))
        self.crop_coords = (self.crop_start_x, self.crop_start_y, self.crop_end_x, self.crop_end_y)
        self.show_cropped_image()
        self.update_parameters()

    def show_cropped_image(self):
        self.tk_cropped_image = ImageTk.PhotoImage(self.cropped_image)
        self.open_image_window()
    
    def open_image_window(self):
        self.image_window = tk.Toplevel(self.root)
        self.image_window.title("Image Window")
        
        self.canvas = tk.Canvas(self.image_window, width=self.tk_cropped_image.width(), height=self.tk_cropped_image.height())
        self.canvas.pack()
        
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_cropped_image)
        self.canvas.image = self.tk_cropped_image  # To prevent garbage collection
        self.canvas.create_line(0, self.baseline_y, self.tk_cropped_image.width(), self.baseline_y, fill='red', width=2)
        
        self.baseline_slider.config(to=self.tk_cropped_image.height())
    
    def update_image_window(self):
        if hasattr(self, 'image_window'):
            self.canvas.config(width=self.tk_cropped_image.width(), height=self.tk_cropped_image.height())
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_cropped_image)
            self.canvas.image = self.tk_cropped_image  # To prevent garbage collection
            self.canvas.create_line(0, self.baseline_y, self.tk_cropped_image.width(), self.baseline_y, fill='red', width=2)
            self.baseline_slider.config(to=self.tk_cropped_image.height())
    
    def save_cropped_image(self):
        self.crop_window.destroy()
        self.rotate_entry.delete(0, tk.END)
        self.rotate_entry.insert(0, str(self.rotation_angle))
    
    def update_parameters(self):
        params = f"Crop Coords: {self.crop_coords}, Rotation: {self.rotation_angle}°, Baseline: {self.baseline_y}"
        self.param_display.config(text=params)
    
    def set_baseline(self, value):
        self.baseline_y = int(value)
        if hasattr(self, 'tk_cropped_image'):
            self.update_image_window()
        self.update_parameters()

    def add_to_queue(self):
        if self.selected_videos and hasattr(self, 'target_path'):
            self.queue.append((self.selected_videos.pop(0), self.target_path))
            # messagebox.showinfo("Queue", "Video added to queue.")
        else:
            messagebox.showwarning("Warning", "Please select a video and a target path first.")
    
    def start_analysis(self):
        if self.queue:
            for video, target in self.queue:
                self.analyze_video(video, target)
            messagebox.showinfo("Analysis", "Analysis completed.")
        else:
            messagebox.showwarning("Warning", "Queue is empty.")
    
    def analyze_video(self, video, target):
        # Hier kommt dein Analysecode rein
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoAnalysisGUI(root)
    root.mainloop()
