#!/usr/bin/env python3
"""
Synchronized Multi-Video Player
A GUI application for playing multiple videos simultaneously with synchronized controls
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import os
from pathlib import Path
import threading
import time


class VideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Synchronized Video Player")
        self.root.geometry("1200x800")
        
        # Video state
        self.videos = []  # List of video capture objects
        self.video_paths = []  # List of video file paths
        self.video_titles = []  # List of video titles
        self.current_frames = []  # Current frame for each video
        self.total_frames = []  # Total frames for each video
        self.fps_list = []  # FPS for each video
        self.frame_indices = []  # Current frame index for each video
        
        # Playback state
        self.is_playing = False
        self.current_frame_index = 0
        self.max_frames = 0
        
        # GUI elements
        self.video_labels = []
        self.title_labels = []
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI layout"""
        # Control frame at the top - make it taller and fix packing
        control_frame = tk.Frame(self.root, bg='#1a1a1a')
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Simple white button styling
        btn_style = {
            'bg': 'white',
            'fg': 'black',
            'activebackground': '#e0e0e0',
            'activeforeground': 'black',
            'font': ('Arial', 10, 'bold'),
            'relief': tk.RAISED,
            'bd': 1,
            'padx': 18,
            'pady': 10
        }
        
        # Secondary button style (same as primary)
        secondary_btn_style = {
            'bg': 'white',
            'fg': 'black',
            'activebackground': '#e0e0e0',
            'activeforeground': 'black',
            'font': ('Arial', 10, 'bold'),
            'relief': tk.RAISED,
            'bd': 1,
            'padx': 18,
            'pady': 10
        }
        
        # Accent button style (same as primary)
        accent_btn_style = {
            'bg': 'white',
            'fg': 'black',
            'activebackground': '#e0e0e0',
            'activeforeground': 'black',
            'font': ('Arial', 10, 'bold'),
            'relief': tk.RAISED,
            'bd': 1,
            'padx': 18,
            'pady': 10
        }
        
        # Load videos button
        load_btn = tk.Button(
            control_frame,
            text="📁 Load Videos",
            command=self.load_videos,
            **accent_btn_style
        )
        load_btn.pack(side=tk.LEFT, padx=5)
        
        # Add hover effects
        def on_enter_accent(e):
            load_btn['bg'] = '#e0e0e0'
        def on_leave_accent(e):
            load_btn['bg'] = 'white'
        load_btn.bind('<Enter>', on_enter_accent)
        load_btn.bind('<Leave>', on_leave_accent)
        
        # Playback controls
        self.play_btn = tk.Button(
            control_frame,
            text="▶ Play",
            command=self.toggle_play,
            **btn_style
        )
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        def on_enter_play(e):
            self.play_btn['bg'] = '#e0e0e0'
        def on_leave_play(e):
            self.play_btn['bg'] = 'white'
        self.play_btn.bind('<Enter>', on_enter_play)
        self.play_btn.bind('<Leave>', on_leave_play)
        
        # Frame backward
        backward_btn = tk.Button(
            control_frame,
            text="⏮ Prev",
            command=self.prev_frame,
            **secondary_btn_style
        )
        backward_btn.pack(side=tk.LEFT, padx=5)
        
        def on_enter_back(e):
            backward_btn['bg'] = '#e0e0e0'
        def on_leave_back(e):
            backward_btn['bg'] = 'white'
        backward_btn.bind('<Enter>', on_enter_back)
        backward_btn.bind('<Leave>', on_leave_back)
        
        # Frame forward
        forward_btn = tk.Button(
            control_frame,
            text="Next ⏭",
            command=self.next_frame,
            **secondary_btn_style
        )
        forward_btn.pack(side=tk.LEFT, padx=5)
        
        def on_enter_forward(e):
            forward_btn['bg'] = '#e0e0e0'
        def on_leave_forward(e):
            forward_btn['bg'] = 'white'
        forward_btn.bind('<Enter>', on_enter_forward)
        forward_btn.bind('<Leave>', on_leave_forward)
        
        # Reset button
        reset_btn = tk.Button(
            control_frame,
            text="⟲ Reset",
            command=self.reset_videos,
            **secondary_btn_style
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        def on_enter_reset(e):
            reset_btn['bg'] = '#e0e0e0'
        def on_leave_reset(e):
            reset_btn['bg'] = 'white'
        reset_btn.bind('<Enter>', on_enter_reset)
        reset_btn.bind('<Leave>', on_leave_reset)
        
        # Frame counter with modern styling
        self.frame_label = tk.Label(
            control_frame,
            text="Frame: 0 / 0",
            bg='#1a1a1a',
            fg='#f0f0f0',
            font=('Arial', 11, 'bold')
        )
        self.frame_label.pack(side=tk.LEFT, padx=20)
        
        # Video counter with modern styling
        self.video_count_label = tk.Label(
            control_frame,
            text="Videos: 0",
            bg='#1a1a1a',
            fg='#0ea5e9',
            font=('Arial', 11, 'bold')
        )
        self.video_count_label.pack(side=tk.LEFT, padx=10)
        
        # Search/Filter section (on right side) with modern styling
        search_label = tk.Label(
            control_frame,
            text="🔍",
            bg='#1a1a1a',
            fg='#f0f0f0',
            font=('Arial', 12)
        )
        search_label.pack(side=tk.RIGHT, padx=(5, 2))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_videos())
        
        # Modern search entry
        search_entry = tk.Entry(
            control_frame,
            textvariable=self.search_var,
            bg='#2d3748',
            fg='white',
            font=('Arial', 10),
            width=25,
            insertbackground='white',
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightbackground='#4a5568',
            highlightcolor='#0ea5e9'
        )
        search_entry.pack(side=tk.RIGHT, padx=5, pady=10, ipady=4)
        
        # Video grid container with scrollbar
        container = tk.Frame(self.root, bg='#1a1a1a')
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(container, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.video_frame = tk.Frame(self.canvas, bg='#1a1a1a')
        self.canvas.create_window((0, 0), window=self.video_frame, anchor=tk.NW)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind canvas resize
        self.video_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        
        # Keyboard shortcuts
        self.root.bind('<space>', lambda e: self.toggle_play())
        self.root.bind('<Left>', lambda e: self.prev_frame())
        self.root.bind('<Right>', lambda e: self.next_frame())
        self.root.bind('<Home>', lambda e: self.reset_videos())
        
    def load_videos(self):
        """Load videos from selected folder"""
        folder_path = filedialog.askdirectory(title="Select Folder with Videos")
        
        if not folder_path:
            return
        
        # Clear existing videos
        self.clear_videos()
        
        # Find video files
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'}
        video_files = []
        
        for file in os.listdir(folder_path):
            if Path(file).suffix.lower() in video_extensions:
                video_files.append(os.path.join(folder_path, file))
        
        if not video_files:
            messagebox.showwarning("No Videos", "No video files found in the selected folder.")
            return
        
        # Sort by file modification time (oldest first)
        video_files.sort(key=lambda x: os.path.getmtime(x))
        
        # Load videos
        for video_path in video_files:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                print(f"Warning: Could not open {video_path}")
                continue
            
            self.videos.append(cap)
            self.video_paths.append(video_path)
            
            # Extract title from filename - handle segmentation output naming
            filename = Path(video_path).stem
            
            # Try to extract prompt from segmentation output format
            # Format: "128by128_prompt-{prompt_name}"
            if "prompt-" in filename:
                # Extract the prompt part after "prompt-"
                prompt_part = filename.split("prompt-", 1)[1]
                # Replace underscores with spaces for readability
                title = prompt_part.replace('_', ' ').title()
            else:
                # Use original filename
                title = filename
            
            self.video_titles.append(title)
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            self.total_frames.append(total_frames)
            self.fps_list.append(fps)
            self.frame_indices.append(0)
            
        if not self.videos:
            messagebox.showerror("Error", "Could not load any videos.")
            return
        
        # Set max frames
        self.max_frames = min(self.total_frames) if self.total_frames else 0
        
        # Create video grid
        self.create_video_grid()
        
        # Load first frame for all videos
        self.load_all_frames(0)
        
        # Update video count
        self.video_count_label.config(text=f"Videos: {len(self.videos)}")
        
        messagebox.showinfo("Success", f"Loaded {len(self.videos)} video(s)")
        
    def filter_videos(self):
        """Filter displayed videos based on search text"""
        if not self.videos:
            return
        
        search_text = self.search_var.get().lower().strip()
        
        # If search is empty, show all videos
        if not search_text:
            for i, container in enumerate(self.video_labels):
                container.master.grid()
            filtered_count = len(self.videos)
        else:
            # Hide videos that don't match the search
            filtered_count = 0
            for i, (title, container) in enumerate(zip(self.video_titles, self.video_labels)):
                if search_text in title.lower():
                    container.master.grid()
                    filtered_count += 1
                else:
                    container.master.grid_remove()
        
        # Update video count
        if search_text:
            self.video_count_label.config(text=f"Videos: {filtered_count}/{len(self.videos)}")
        else:
            self.video_count_label.config(text=f"Videos: {len(self.videos)}")
        
    def create_video_grid(self):
        """Create grid layout for videos"""
        # Clear existing widgets
        for widget in self.video_frame.winfo_children():
            widget.destroy()
        
        self.video_labels = []
        self.title_labels = []
        
        # Calculate grid dimensions optimized for many videos
        num_videos = len(self.videos)
        
        # Use 8 columns for wide monitors
        cols = 8
        
        # Use 3/4 of original size: 300x225 instead of 400x300
        max_width, max_height = 300, 225
        
        # Store these for use in load_all_frames
        self.display_width = max_width
        self.display_height = max_height
        
        for i, (video, title) in enumerate(zip(self.videos, self.video_titles)):
            row = i // cols
            col = i % cols
            
            # Container for each video
            video_container = tk.Frame(self.video_frame, bg='#2b2b2b', relief=tk.RAISED, bd=2)
            video_container.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            # Video label
            video_label = tk.Label(video_container, bg='black')
            video_label.pack(padx=5, pady=5)
            self.video_labels.append(video_label)
            
            # Title label
            title_label = tk.Label(
                video_container,
                text=title,
                bg='#2b2b2b',
                fg='white',
                font=('Arial', 14, 'bold'),
                wraplength=max_width - 10
            )
            title_label.pack(pady=(0, 5), padx=5)
            self.title_labels.append(title_label)
        
        # Configure grid weights
        for i in range(cols):
            self.video_frame.grid_columnconfigure(i, weight=1)
    
    def load_all_frames(self, frame_index):
        """Load and display a specific frame for all videos"""
        if not self.videos:
            return
        
        # Clamp frame index
        frame_index = max(0, min(frame_index, self.max_frames - 1))
        self.current_frame_index = frame_index
        
        # Update frame counter
        self.frame_label.config(text=f"Frame: {frame_index + 1} / {self.max_frames}")
        
        for i, cap in enumerate(self.videos):
            # Set frame position
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            
            # Read frame
            ret, frame = cap.read()
            
            if ret:
                # Resize frame to fit display using dynamic dimensions
                height, width = frame.shape[:2]
                max_width = getattr(self, 'display_width', 400)
                max_height = getattr(self, 'display_height', 300)
                
                scale = min(max_width / width, max_height / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                frame = cv2.resize(frame, (new_width, new_height))
                
                # Convert to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PhotoImage
                img = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=img)
                
                # Update label
                self.video_labels[i].config(image=photo)
                self.video_labels[i].image = photo  # Keep reference
    
    def toggle_play(self):
        """Toggle play/pause"""
        if not self.videos:
            return
        
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_btn.config(text="⏸ Pause")
            threading.Thread(target=self.play_videos, daemon=True).start()
        else:
            self.play_btn.config(text="▶ Play")
    
    def play_videos(self):
        """Play videos continuously"""
        if not self.videos or not self.fps_list:
            return
        
        # Use the minimum FPS to sync all videos
        target_fps = min(self.fps_list)
        frame_delay = 1.0 / target_fps if target_fps > 0 else 0.033
        
        while self.is_playing and self.current_frame_index < self.max_frames - 1:
            start_time = time.time()
            
            self.current_frame_index += 1
            self.load_all_frames(self.current_frame_index)
            
            # Maintain frame rate
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_delay - elapsed)
            time.sleep(sleep_time)
        
        # Stop playing when reaching the end
        if self.current_frame_index >= self.max_frames - 1:
            self.is_playing = False
            self.play_btn.config(text="▶ Play")
    
    def next_frame(self):
        """Advance one frame forward"""
        if not self.videos:
            return
        
        self.is_playing = False
        self.play_btn.config(text="▶ Play")
        
        if self.current_frame_index < self.max_frames - 1:
            self.load_all_frames(self.current_frame_index + 1)
    
    def prev_frame(self):
        """Go one frame backward"""
        if not self.videos:
            return
        
        self.is_playing = False
        self.play_btn.config(text="▶ Play")
        
        if self.current_frame_index > 0:
            self.load_all_frames(self.current_frame_index - 1)
    
    def reset_videos(self):
        """Reset all videos to frame 0"""
        if not self.videos:
            return
        
        self.is_playing = False
        self.play_btn.config(text="▶ Play")
        self.load_all_frames(0)
    
    def clear_videos(self):
        """Clear all loaded videos"""
        self.is_playing = False
        
        # Release video captures
        for cap in self.videos:
            cap.release()
        
        # Clear data
        self.videos = []
        self.video_paths = []
        self.video_titles = []
        self.total_frames = []
        self.fps_list = []
        self.frame_indices = []
        self.current_frame_index = 0
        self.max_frames = 0
        
        # Clear GUI
        for widget in self.video_frame.winfo_children():
            widget.destroy()
        
        self.video_labels = []
        self.title_labels = []
        
        self.frame_label.config(text="Frame: 0 / 0")
    
    def on_closing(self):
        """Cleanup when closing the application"""
        self.is_playing = False
        for cap in self.videos:
            cap.release()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = VideoPlayer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()