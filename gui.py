import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
# from video_processing import VideoProcessor  # Uncomment if you have this module

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar_v = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar_h = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar_v.set, xscrollcommand=self.scrollbar_h.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar_v.pack(side="right", fill="y")
        self.scrollbar_h.pack(side="bottom", fill="x")

class VideoAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Analysis Tool")
        
        self.selected_videos = []
        self.queue = []
        self.target_path = ""
        
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
        
        # Video selection
        self.video_label = ttk.Label(self.root, text="Select Video:")
        self.video_label.grid(row=0, column=0, padx=10, pady=10)
        self.video_button = ttk.Button(self.root, text="Browse", command=self.select_video)
        self.video_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Target path selection
        self.target_label = ttk.Label(self.root, text="Select Target Path:")
        self.target_label.grid(row=1, column=0, padx=10, pady=10)
        self.target_button = ttk.Button(self.root, text="Browse", command=self.select_target_path)
        self.target_button.grid(row=1, column=1, padx=10, pady=10)
        
        # Image selection and cropping
        self.crop_label = ttk.Label(self.root, text="Crop Image:")
        self.crop_label.grid(row=2, column=0, padx=10, pady=10)
        self.crop_button = ttk.Button(self.root, text="Select Image from Video", command=self.select_image_from_video)
        self.crop_button.grid(row=2, column=1, padx=10, pady=10)
        
        # Image rotation
        self.rotate_label = ttk.Label(self.root, text="Rotate Image (degrees):")
        self.rotate_label.grid(row=3, column=0, padx=10, pady=10)
        self.rotate_entry = ttk.Entry(self.root)
        self.rotate_entry.grid(row=3, column=1, padx=10, pady=10)
        self.rotate_entry.bind("<Return>", self.rotate_cropped_image)
        
        # Baseline selection
        self.baseline_label = ttk.Label(self.root, text="Select Baseline:")
        self.baseline_label.grid(row=4, column=0, padx=10, pady=10)
        self.baseline_slider = tk.Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, length=300, command=self.set_baseline)
        self.baseline_slider.grid(row=4, column=1, padx=10, pady=10)
        
        # Threshold settings
        self.threshold1_label = ttk.Label(self.root, text="Threshold 1:")
        self.threshold1_label.grid(row=5, column=0, padx=10, pady=10)
        self.threshold1_slider = tk.Scale(self.root, from_=0, to=255, orient=tk.HORIZONTAL, length=300)
        self.threshold1_slider.grid(row=5, column=1, padx=10, pady=10)
        
        self.threshold2_label = ttk.Label(self.root, text="Threshold 2:")
        self.threshold2_label.grid(row=6, column=0, padx=10, pady=10)
        self.threshold2_slider = tk.Scale(self.root, from_=0, to=255, orient=tk.HORIZONTAL, length=300)
        self.threshold2_slider.grid(row=6, column=1, padx=10, pady=10)
        
        # Parameter display
        self.param_label = ttk.Label(self.root, text="Parameters:")
        self.param_label.grid(row=7, column=0, padx=10, pady=10)
        
        self.param_display = tk.Text(self.root, height=10, width=60, wrap=tk.WORD)
        self.param_display.grid(row=7, column=1, padx=10, pady=10)
        self.param_display.config(state=tk.DISABLED)
        
        # Queue and start analysis
        self.queue_button = ttk.Button(self.root, text="Add to Queue", command=self.add_to_queue)
        self.queue_button.grid(row=8, column=0, padx=10, pady=10)
        
        self.start_button = ttk.Button(self.root, text="Start Analysis", command=self.start_analysis)
        self.start_button.grid(row=8, column=1, padx=10, pady=10)

    def select_video(self):
        video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
        if video_path:
            self.selected_videos.append(video_path)
            self.update_parameters()
    
    def select_target_path(self):
        target_path = filedialog.askdirectory()
        if target_path:
            self.target_path = target_path
            self.update_parameters()
    
    def select_image_from_video(self):
        if not self.selected_videos:
            messagebox.showwarning("Warning", "Please select a video first.")
            return
        
        video_path = self.selected_videos[-1]
        self.cap = cv2.VideoCapture(video_path)
        
        self.video_window = tk.Toplevel(self.root)
        self.video_window.title("Select Frame")
        self.video_window.geometry("800x600")  # Set a default size
        self.video_window.minsize(400, 300)  # Set minimum size
        
        # Create a scrollable frame
        scrollable_frame = ScrollableFrame(self.video_window)
        scrollable_frame.pack(fill=tk.BOTH, expand=True)

        self.video_label = ttk.Label(scrollable_frame.scrollable_frame)
        self.video_label.pack()

        self.pause = False

        self.timeline = tk.Scale(scrollable_frame.scrollable_frame, from_=0, to=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))-1, orient=tk.HORIZONTAL, length=400, command=self.set_frame)
        self.timeline.pack()

        controls_frame = ttk.Frame(scrollable_frame.scrollable_frame)
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

        self.select_frame_button = ttk.Button(scrollable_frame.scrollable_frame, text="Select Frame", command=self.capture_frame)
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
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)

        # Resize the image to fit the label
        img = img.resize((600, 400), Image.LANCZOS)
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
        self.selected_frame_number = self.current_frame_pos  # Store the frame number
        self.cap.release()
        self.video_window.destroy()
        frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        self.show_frame_for_cropping(frame_rgb)

    def show_frame_for_cropping(self, frame):
        self.original_image = Image.fromarray(frame)
        self.rotated_image = self.original_image
        self.crop_window = tk.Toplevel(self.root)
        self.crop_window.title("Crop Image")
        self.crop_window.geometry("800x600")
        self.crop_window.minsize(400, 300)
        
        # Create a scrollable frame
        scrollable_frame = ScrollableFrame(self.crop_window)
        scrollable_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas_crop = tk.Canvas(scrollable_frame.scrollable_frame, width=self.rotated_image.width, height=self.rotated_image.height)
        self.canvas_crop.pack()

        self.rotate_label_crop = ttk.Label(scrollable_frame.scrollable_frame, text="Rotate Image (degrees):")
        self.rotate_label_crop.pack(pady=5)

        self.rotate_entry_crop = ttk.Entry(scrollable_frame.scrollable_frame)
        self.rotate_entry_crop.pack(pady=5)
        self.rotate_entry_crop.bind("<Return>", self.rotate_image_entry_crop)

        self.show_rotated_image()

        self.canvas_crop.bind("<Button-1>", self.start_crop)
        self.canvas_crop.bind("<B1-Motion>", self.do_crop)
        self.canvas_crop.bind("<ButtonRelease-1>", self.end_crop)

        self.crop_rectangle = None
        self.crop_start_x = None
        self.crop_start_y = None

        self.save_button_in_crop = ttk.Button(scrollable_frame.scrollable_frame, text="Save and Continue", command=self.preview_cropped_image)
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
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        max_width = int(screen_width * 0.8)
        max_height = int(screen_height * 0.8)
        
        if self.rotated_image.width > max_width or self.rotated_image.height > max_height:
            self.scale_factor = min(max_width / self.rotated_image.width, max_height / self.rotated_image.height)
            new_size = (int(self.rotated_image.width * self.scale_factor), int(self.rotated_image.height * self.scale_factor))
            resized_image = self.rotated_image.resize(new_size, Image.LANCZOS)
        else:
            self.scale_factor = 1
            resized_image = self.rotated_image

        self.tk_image = ImageTk.PhotoImage(resized_image)
        self.canvas_crop.config(width=resized_image.width, height=resized_image.height)
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

        # Convert the coordinates from the displayed (scaled) image to the rotated image
        orig_crop_start_x = int(self.crop_start_x / self.scale_factor)
        orig_crop_start_y = int(self.crop_start_y / self.scale_factor)
        orig_crop_end_x = int(self.crop_end_x / self.scale_factor)
        orig_crop_end_y = int(self.crop_end_y / self.scale_factor)

        # Ensure that x1, y1 are the top-left coordinates and x2, y2 are the bottom-right
        x1 = min(orig_crop_start_x, orig_crop_end_x)
        y1 = min(orig_crop_start_y, orig_crop_end_y)
        x2 = max(orig_crop_start_x, orig_crop_end_x)
        y2 = max(orig_crop_start_y, orig_crop_end_y)

        self.crop_coords = (x1, y1, x2, y2)
        self.cropped_image = self.rotated_image.crop(self.crop_coords)
        self.update_parameters()

    def preview_cropped_image(self):
        self.tk_cropped_image = ImageTk.PhotoImage(self.cropped_image)
        self.cropped_image_window = tk.Toplevel(self.root)
        self.cropped_image_window.title("Cropped Image Preview")
        
        self.cropped_image_canvas = tk.Canvas(self.cropped_image_window, width=self.tk_cropped_image.width(), height=self.tk_cropped_image.height())
        self.cropped_image_canvas.pack()
        
        self.cropped_image_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_cropped_image)
        self.cropped_image_canvas.image = self.tk_cropped_image  # To prevent garbage collection
        
        # Add buttons to confirm or readjust the cropping
        self.confirm_button = ttk.Button(self.cropped_image_window, text="Confirm", command=self.confirm_cropping)
        self.confirm_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.readjust_button = ttk.Button(self.cropped_image_window, text="Readjust", command=self.readjust_cropping)
        self.readjust_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def confirm_cropping(self):
        self.cropped_image_window.destroy()
        self.crop_window.destroy()
        self.open_image_window()
        self.rotate_entry.delete(0, tk.END)
        self.rotate_entry.insert(0, str(self.rotation_angle))

    def readjust_cropping(self):
        self.cropped_image_window.destroy()
    
    def open_image_window(self):
        self.image_window = tk.Toplevel(self.root)
        self.image_window.title("Cropped Image for Baseline Selection")
        self.image_window.geometry("800x600")
        self.image_window.minsize(400, 300)
        
        # Create a scrollable frame
        scrollable_frame = ScrollableFrame(self.image_window)
        scrollable_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(scrollable_frame.scrollable_frame, width=self.tk_cropped_image.width(), height=self.tk_cropped_image.height())
        self.canvas.pack()
        
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_cropped_image)
        self.canvas.image = self.tk_cropped_image  # To prevent garbage collection
        self.canvas.create_line(0, self.baseline_y, self.tk_cropped_image.width(), self.baseline_y, fill='red', width=2)
        
        self.baseline_slider.config(to=self.tk_cropped_image.height())

    def rotate_cropped_image(self, event):
        if hasattr(self, 'original_image') and hasattr(self, 'crop_coords'):
            try:
                new_angle = int(self.rotate_entry.get())
                self.rotation_angle = new_angle
                # Rotate the original image first
                rotated_image = self.original_image.rotate(self.rotation_angle, expand=True)
                # Crop the rotated image
                cropped_image = rotated_image.crop(self.crop_coords)
                self.cropped_image = cropped_image
                self.tk_cropped_image = ImageTk.PhotoImage(self.cropped_image)
                self.update_image_window()
                self.update_parameters()
            except ValueError:
                messagebox.showwarning("Warning", "Please enter a valid integer.")
        else:
            messagebox.showwarning("Warning", "Please crop an image first.")

    def update_image_window(self):
        if hasattr(self, 'image_window'):
            self.canvas.config(width=self.tk_cropped_image.width(), height=self.tk_cropped_image.height())
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_cropped_image)
            self.canvas.image = self.tk_cropped_image  # To prevent garbage collection
            self.canvas.create_line(0, self.baseline_y, self.tk_cropped_image.width(), self.baseline_y, fill='red', width=2)
            self.baseline_slider.config(to=self.tk_cropped_image.height())

    def update_parameters(self):
        self.param_display.config(state=tk.NORMAL)
        self.param_display.delete(1.0, tk.END)
        selected_videos_str = "\n".join(self.selected_videos)
        crop_x1, crop_y1, crop_x2, crop_y2 = self.crop_coords if self.crop_coords else (None, None, None, None)
        if None not in (crop_x1, crop_y1, crop_x2, crop_y2):
            crop_x = crop_x1
            crop_y = crop_y1
            crop_width = crop_x2 - crop_x1
            crop_height = crop_y2 - crop_y1
            crop_coords_str = (f"Crop Coords:\n"
                               f" - x1: {crop_x1}, y1: {crop_y1}, x2: {crop_x2}, y2: {crop_y2}\n"
                               f" - x: {crop_x}, y: {crop_y}, width: {crop_width}, height: {crop_height}")
        else:
            crop_coords_str = "Crop Coords: None"

        params = (
            f"Selected Videos:\n{selected_videos_str}\n\n"
            f"Selected Frame Number: {getattr(self, 'selected_frame_number', 'Not Selected')}\n\n"
            f"Target Path:\n{self.target_path}\n\n"
            f"{crop_coords_str}\n\n"
            f"Rotation: {self.rotation_angle}°\n"
            f"Baseline: {self.baseline_y}"
        )
        self.param_display.insert(tk.END, params)
        self.param_display.config(state=tk.DISABLED)

    def reset_parameters(self):
        self.selected_videos = []
        self.target_path = ""
        self.crop_coords = None
        self.rotation_angle = 0
        self.baseline_y = 0
        self.rotate_entry.delete(0, tk.END)
        self.baseline_slider.set(0)
        self.update_parameters()

    def set_baseline(self, value):
        self.baseline_y = int(value)
        if hasattr(self, 'tk_cropped_image'):
            self.update_image_window()
        self.update_parameters()

    def add_to_queue(self):
        if self.selected_videos and self.target_path:
            self.queue.append((self.selected_videos.copy(), self.target_path))
            self.reset_parameters()
        else:
            messagebox.showwarning("Warning", "Please select a video and a target path first.")
    
    def start_analysis(self):
        if self.queue:
            for video, target in self.queue:
                pass  # VideoProcessor.analyze_video(video, target)  # Uncomment when you have this function
            messagebox.showinfo("Analysis", "Analysis completed.")
        else:
            messagebox.showwarning("Warning", "Queue is empty.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoAnalysisGUI(root)
    root.mainloop()