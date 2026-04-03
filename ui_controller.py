import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog

class UIController:
    """
    Manages a Tkinter window with two panels that light up based on gaze
    and allow loading custom images.
    """
    def __init__(self):
        # Colors
        self.COLOR_HIGHLIGHT = "lightgreen"
        self.COLOR_HIGHLIGHT_ALT = "red"
        self.COLOR_DEFAULT = "SystemButtonFace" # Default widget color
        self.default_geometry = "1280x720"

        self.root = tk.Tk()
        self.root.title("Response Control")

        # The window starts with the default dimensions.
        self.fullscreen_state = False
        self.root.geometry(self.default_geometry)

        # Add bindings for F11 (toggle fullscreen) and ESC (exit fullscreen)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)

        # Main frame to hold the two quadrants
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # YES Quadrant (Left)
        self.si_label = tk.Label(main_frame, text="YES", font=("Helvetica", 36, "bold"), borderwidth=2, relief="solid")
        self.si_label.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # NO Quadrant (Right)
        self.no_label = tk.Label(main_frame, text="NO", font=("Helvetica", 36, "bold"), borderwidth=2, relief="solid")
        self.no_label.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # References to loaded images to prevent them from being garbage collected
        self.si_photo = None
        self.no_photo = None

        # State to control the analysis
        self.analysis_running = False
        self.webcam_visible = False # Webcam is hidden by default

        # --- Author/Footer Frame ---
        footer_frame = tk.Frame(self.root)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 5))
        author_label = tk.Label(footer_frame, text="Copyright (c) 2026 AntimoFerraro", font=("Helvetica", 8), fg="gray")
        author_label.pack(side=tk.RIGHT)

        # --- Controls Frame ---
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=20)

        # Label for the slider
        threshold_label = tk.Label(controls_frame, text="Gaze Threshold (degrees):", font=("Helvetica", 12))
        threshold_label.pack(side=tk.LEFT, padx=(0, 10))

        # Threshold slider
        self.threshold_slider = tk.Scale(
            controls_frame,
            from_=1,
            to=30,
            orient=tk.HORIZONTAL,
            resolution=0.5
        )
        self.threshold_slider.set(10.0) # Default value
        self.threshold_slider.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Start/Stop toggle button
        self.toggle_button = tk.Button(controls_frame, text="Start", command=self.toggle_analysis, width=10)
        self.toggle_button.pack(side=tk.RIGHT, padx=(20, 5))

        # Buttons to load images
        self.si_button = tk.Button(controls_frame, text="Load Img. 2", command=self.load_image_no)
        self.si_button.pack(side=tk.RIGHT, padx=5)
        self.no_button = tk.Button(controls_frame, text="Load Img. 1", command=self.load_image_si)
        self.no_button.pack(side=tk.RIGHT, padx=5)

        # Webcam toggle button
        self.webcam_button = tk.Button(controls_frame, text="Show Webcam", command=self.toggle_webcam_visibility, width=12)
        self.webcam_button.pack(side=tk.RIGHT, padx=5)
        # Set initial state
        self.update_highlight("Center")

    # --- NEW FUNCTIONS FOR LOADING IMAGES ---
    def load_image_si(self):
        """Opens a file dialog to load the 'YES' image."""
        self._handle_image_load(self.si_label)

    def load_image_no(self):
        """Opens a file dialog to load the 'NO' image."""
        self._handle_image_load(self.no_label)

    def _handle_image_load(self, target_label):
        """
        Handles the selection and loading of an image for a given label.
        """
        filepath = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if not filepath:
            return  # User cancelled the selection

        photo = self._load_image_for_label(target_label, filepath)
        if photo:
            if target_label is self.si_label:
                self.si_photo = photo
            else:
                self.no_photo = photo
            
            target_label.config(image=photo, text="")
            target_label.image = photo # Keep a reference

    def _load_image_for_label(self, label, filepath):
        """
        Loads an image and resizes it to a fixed size (500x500),
        maintaining the aspect ratio and adding transparent padding (letterboxing).
        """
        try:
            TARGET_SIZE = (500, 500)  # Fixed size for the final image

            image = Image.open(filepath)

            img_copy = image.copy()

            # Ridimensiona l'immagine mantenendo l'aspect ratio per adattarla a TARGET_SIZE
            img_copy.thumbnail(TARGET_SIZE, Image.Resampling.LANCZOS)

            # Create a transparent canvas with the exact dimensions of TARGET_SIZE
            canvas = Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))

            # Calculate the position to center the image on the canvas
            paste_x = (TARGET_SIZE[0] - img_copy.width) // 2
            paste_y = (TARGET_SIZE[1] - img_copy.height) // 2

            # Paste the resized image onto the canvas, using the alpha channel if present
            if img_copy.mode == 'RGBA':
                canvas.paste(img_copy, (paste_x, paste_y), img_copy)
            else:
                canvas.paste(img_copy, (paste_x, paste_y))

            return ImageTk.PhotoImage(canvas)
        except Exception as e:
            print(f"Error loading image '{filepath}': {e}")
            return None

    def toggle_fullscreen(self, event=None):
        """Toggles fullscreen mode."""
        self.fullscreen_state = not self.fullscreen_state
        self.root.attributes("-fullscreen", self.fullscreen_state)
        # If we exit fullscreen, set the default geometry
        if not self.fullscreen_state:
            self.root.geometry(self.default_geometry)
        return "break"

    def end_fullscreen(self, event=None):
        """Exits fullscreen mode if active."""
        if self.fullscreen_state:
            self.fullscreen_state = False
            self.root.attributes("-fullscreen", False)
            self.root.geometry(self.default_geometry)
        return "break"

    def get_threshold(self):
        """Returns the current value of the threshold slider."""
        return self.threshold_slider.get()

    def is_analysis_running(self):
        """Returns True if the analysis is running."""
        return self.analysis_running

    def is_webcam_visible(self):
        """Returns True if the webcam feed should be visible."""
        return self.webcam_visible

    def toggle_analysis(self):
        """Starts or stops the analysis process."""
        self.analysis_running = not self.analysis_running
        if self.analysis_running:
            self.toggle_button.config(text="Stop", bg=self.COLOR_HIGHLIGHT_ALT)
        else:
            self.toggle_button.config(text="Start", bg=self.COLOR_DEFAULT)
            self.update_highlight("Center") # Reset the UI when stopped

    def toggle_webcam_visibility(self):
        """Toggles the visibility of the webcam feed window."""
        self.webcam_visible = not self.webcam_visible
        self.webcam_button.config(text="Hide Webcam" if self.webcam_visible else "Show Webcam")

    def update_highlight(self, direction):
        """
        Updates the background color of the quadrants based on the direction.
        'Right'   -> highlights YES (left)
        'Left'    -> highlights NO (right)
        'Center'  -> resets both
        """
        if direction == "Right":
            self.si_label.config(bg=self.COLOR_HIGHLIGHT)
            self.no_label.config(bg=self.COLOR_DEFAULT)
        elif direction == "Left":
            self.si_label.config(bg=self.COLOR_DEFAULT)
            self.no_label.config(bg=self.COLOR_HIGHLIGHT)
        else: # Center or N/A
            self.si_label.config(bg=self.COLOR_DEFAULT)
            self.no_label.config(bg=self.COLOR_DEFAULT)