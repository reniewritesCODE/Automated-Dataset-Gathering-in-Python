import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import cv2
import os
from PIL import Image, ImageTk

# ==========================================    
# CONFIGURATION
# ==========================================
BASE_SAVE_DIR = "Robusta_Dataset"

class BeanDatasetCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robusta Bean Dataset Capture System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1e1e1e")

        # --- Variables for Inputs ---
        self.var_defect_class = tk.StringVar(value="withered")
        self.var_cam_index = tk.StringVar(value="0") # Usually 0 for webcam, 1 or 2 for DSLR
        self.var_base_dir = tk.StringVar(value=BASE_SAVE_DIR)

        # --- State Variables ---
        self.current_frame = None
        self.cap = None
        
        # Ensure base directory exists
        if not os.path.exists(BASE_SAVE_DIR):
            os.makedirs(BASE_SAVE_DIR)

        self.setup_ui()
        
        # Initialize Camera shortly after UI loads
        self.root.after(100, self.start_camera)
        
        # Handle window close to release camera
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Arial", 11))
        
        # === LAYOUT ===
        # Left: Video & Controls
        left_panel = tk.Frame(self.root, bg="#1e1e1e")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Video Display
        self.video_label = tk.Label(left_panel, bg="black", text="Loading Camera...", fg="white", font=("Arial", 16))
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Controls Area (Bottom Left)
        control_frame = tk.Frame(left_panel, bg="#2b2b2b", padx=10, pady=15)
        control_frame.pack(fill=tk.X, pady=10)

        # Inputs Setup
        tk.Label(control_frame, text="Defect Class:", bg="#2b2b2b", fg="#aaa", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_class = tk.Entry(control_frame, textvariable=self.var_defect_class, bg="#444", fg="white", width=20, font=("Arial", 12))
        self.entry_class.grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(control_frame, text="Camera Index:", bg="#2b2b2b", fg="#aaa", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_cam = tk.Entry(control_frame, textvariable=self.var_cam_index, bg="#444", fg="white", width=5)
        self.entry_cam.grid(row=1, column=1, sticky="w", padx=5)
        
        self.btn_reconnect = tk.Button(control_frame, text="Reconnect Camera", command=self.start_camera,
                                       bg="#555", fg="white", relief="flat", padx=10)
        self.btn_reconnect.grid(row=1, column=1, sticky="e", padx=5)

        # Capture Button (Big)
        self.btn_capture = tk.Button(control_frame, text="📸 CAPTURE IMAGE", command=self.capture_image, 
                                   bg="#28a745", fg="white", font=("Arial", 14, "bold"), relief="flat", padx=20, pady=15)
        self.btn_capture.grid(row=0, column=2, rowspan=2, padx=30)
        
        # Bind the SPACEBAR to capture an image as well
        self.root.bind('<space>', lambda event: self.capture_image())


        # === RIGHT PANEL (Logs & Status) ===
        right_panel = tk.Frame(self.root, bg="#2b2b2b", width=350)
        right_panel.pack_propagate(False)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        tk.Label(right_panel, text="Capture Logs", bg="#2b2b2b", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.txt_log = scrolledtext.ScrolledText(right_panel, bg="#1e1e1e", fg="#00ff00", height=30, font=("Consolas", 10))
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_message("System Initialized.")
        self.log_message(f"Base Directory: {os.path.abspath(BASE_SAVE_DIR)}")
        self.log_message("Tip: You can press SPACEBAR to capture.")

    def start_camera(self):
        # Release existing camera if open
        if self.cap is not None:
            self.cap.release()

        try:
            cam_idx = int(self.var_cam_index.get())
            # cv2.CAP_DSHOW is generally best for Windows to get direct show devices (DSLRs)
            self.cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW) 
            
            if not self.cap.isOpened():
                self.video_label.config(text=f"Error: Camera {cam_idx} not found.\nTry index 0, 1, or 2.", image='')
                self.log_message(f"ERROR: Could not open camera {cam_idx}.", error=True)
            else:
                # Request High Resolution from the DSLR/Webcam
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                
                # Check actual resolution granted by the camera
                actual_w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                actual_h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                self.log_message(f"Camera {cam_idx} Connected. Resolution: {int(actual_w)}x{int(actual_h)}")
                
                self.video_loop()
        except ValueError:
            messagebox.showerror("Invalid Input", "Camera index must be an integer.")
        except Exception as e:
            self.log_message(f"Cam Error: {e}", error=True)

    def video_loop(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Store the high-res raw frame for saving later
                self.current_frame = frame.copy()

                # Convert for Tkinter Display
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                
                # Resize specifically for the GUI layout so it fits nicely
                img = img.resize((800, 450), Image.Resampling.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk, text='')

        # Repeat every 30 milliseconds
        self.root.after(30, self.video_loop)

    def capture_image(self):
        if self.current_frame is None:
            messagebox.showwarning("Warning", "No camera feed available. Cannot capture.")
            return

        # 1. Get and format the defect class name
        raw_class = self.var_defect_class.get().strip()
        if not raw_class:
            messagebox.showwarning("Warning", "Please enter a Defect Class name first.")
            return
            
        # Clean up the folder name (replace spaces with underscores, lowercase)
        defect_class = raw_class.replace(" ", "_").lower()

        # 2. Create the folder if it doesn't exist
        class_dir = os.path.join(BASE_SAVE_DIR, defect_class)
        if not os.path.exists(class_dir):
            os.makedirs(class_dir)
            self.log_message(f"Created new folder: /{defect_class}")

        # 3. Determine the next increment number
        # Look at all files in the folder to find the current highest number
        existing_files = os.listdir(class_dir)
        count = len(existing_files) + 1

        # 4. Generate filename and full path
        filename = f"{defect_class}_{count}.jpg"
        filepath = os.path.join(class_dir, filename)

        # 5. Save the image (using the high-res current_frame, NOT the resized UI frame)
        success = cv2.imwrite(filepath, self.current_frame)

        if success:
            self.log_message(f"SAVED: {filename}")
            self.flash_screen()
        else:
            self.log_message(f"FAILED to save: {filename}", error=True)

    def log_message(self, msg, error=False):
        self.txt_log.config(state=tk.NORMAL)
        if error:
            self.txt_log.insert(tk.END, f"[!] {msg}\n", "error")
            self.txt_log.tag_config("error", foreground="red")
        else:
            self.txt_log.insert(tk.END, f"> {msg}\n")
            
        self.txt_log.see(tk.END) # Auto-scroll to bottom
        self.txt_log.config(state=tk.DISABLED)

    def flash_screen(self):
        # Brief visual feedback that a picture was taken
        self.video_label.config(bg="white")
        self.root.update()
        self.root.after(50, lambda: self.video_label.config(bg="black"))

    def on_closing(self):
        if self.cap is not None:
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BeanDatasetCaptureApp(root)
    root.mainloop()