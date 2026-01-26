import pygame
import serial
import subprocess
import sys
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os

print("=== ASD Learning System Launcher ===")

BASE_DIR = "/home/pi/asd_learning_system"
GIF_PATH = os.path.join(BASE_DIR, "feedback_gifs")

pygame.init()
pygame.mixer.init()

root = tk.Tk()
root.title("ASD Learning System")
root.attributes("-fullscreen", True)
root.overrideredirect(True)
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
root.configure(bg="#f0f4f8")
root.focus_force()

child_name = ""

def exit_app(event=None):
    print("Exiting launcher...")
    root.destroy()
    sys.exit()

root.bind("<Escape>", exit_app)
root.bind("<Control-q>", exit_app)

# Main container
main_frame = tk.Frame(root, bg="#f0f4f8")
main_frame.pack(expand=True, fill="both")

def launch_level(level_num, name):
    """Launch a specific level with the child's name"""
    print(f"Launching Level {level_num} for {name}")
    root.destroy()
    
    # Pass name as command line argument
    if level_num == 1:
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "level1_enhanced.py"), name])
    elif level_num == 2:
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "level2_enhanced.py"), name])
    elif level_num == 3:
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "level3_enhanced.py"), name])

def show_name_entry():
    """Show name entry screen"""
    for widget in main_frame.winfo_children():
        widget.destroy()
    
    entry_container = tk.Frame(main_frame, bg="#f0f4f8")
    entry_container.pack(expand=True)
    
    # Welcome GIF
    gif_label = tk.Label(entry_container, bg="#f0f4f8")
    gif_label.pack(pady=30)
    
    try:
        gif_path = os.path.join(GIF_PATH, "default_level2.gif")
        gif_image = Image.open(gif_path)
        gif_frames = [
            ImageTk.PhotoImage(frame.resize((500, 350)))
            for frame in ImageSequence.Iterator(gif_image)
        ]
        
        frame_count = [0]
        
        def animate_gif():
            if frame_count[0] < len(gif_frames) and gif_label.winfo_exists():
                gif_label.config(image=gif_frames[frame_count[0]])
                gif_label.image = gif_frames[frame_count[0]]
                frame_count[0] += 1
                root.after(100, animate_gif)
            elif gif_label.winfo_exists():
                gif_label.config(image=gif_frames[-1])
                gif_label.image = gif_frames[-1]
        
        animate_gif()
    except:
        pass
    
    # Title
    title = tk.Label(
        entry_container,
        text="🌟 Welcome to Animal Learning 🌟",
        font=("Arial", 44, "bold"),
        bg="#f0f4f8",
        fg="#2c3e50"
    )
    title.pack(pady=20)
    
    # Name entry
    name_label = tk.Label(
        entry_container,
        text="What's your name?",
        font=("Arial", 32, "bold"),
        bg="#f0f4f8",
        fg="#34495e"
    )
    name_label.pack(pady=15)
    
    name_entry = tk.Entry(
        entry_container,
        font=("Arial", 28),
        width=20,
        justify="center",
        bg="white",
        fg="#2c3e50",
        relief="solid",
        bd=2
    )
    name_entry.pack(pady=15)
    name_entry.focus()
    
    def proceed():
        global child_name
        child_name = name_entry.get().strip()
        if not child_name:
            child_name = "Player"
        show_level_menu()
    
    name_entry.bind("<Return>", lambda e: proceed())
    
    continue_btn = tk.Button(
        entry_container,
        text="CONTINUE",
        font=("Arial", 28, "bold"),
        bg="#3498db",
        fg="white",
        activebackground="#2980b9",
        activeforeground="white",
        relief="raised",
        bd=5,
        padx=40,
        pady=15,
        command=proceed,
        cursor="hand2"
    )
    continue_btn.pack(pady=20)

def show_level_menu():
    """Show level selection menu"""
    for widget in main_frame.winfo_children():
        widget.destroy()
    
    menu_container = tk.Frame(main_frame, bg="#f0f4f8")
    menu_container.pack(expand=True)
    
    # Welcome message
    welcome = tk.Label(
        menu_container,
        text=f"Hello, {child_name}! 👋",
        font=("Arial", 42, "bold"),
        bg="#f0f4f8",
        fg="#2c3e50"
    )
    welcome.pack(pady=30)
    
    instruction = tk.Label(
        menu_container,
        text="Choose Your Learning Level",
        font=("Arial", 32),
        bg="#f0f4f8",
        fg="#34495e"
    )
    instruction.pack(pady=10)
    
    # Level buttons container
    buttons_frame = tk.Frame(menu_container, bg="#f0f4f8")
    buttons_frame.pack(pady=40)
    
    # Level 1 Button
    level1_btn = tk.Button(
        buttons_frame,
        text="📚 LEVEL 1\nFree Learning",
        font=("Arial", 26, "bold"),
        bg="#27ae60",
        fg="white",
        activebackground="#229954",
        activeforeground="white",
        relief="raised",
        bd=6,
        width=18,
        height=4,
        command=lambda: launch_level(1, child_name),
        cursor="hand2"
    )
    level1_btn.grid(row=0, column=0, padx=20, pady=15)
    
    # Level 2 Button
    level2_btn = tk.Button(
        buttons_frame,
        text="🖼️ LEVEL 2\nImage Matching",
        font=("Arial", 26, "bold"),
        bg="#3498db",
        fg="white",
        activebackground="#2980b9",
        activeforeground="white",
        relief="raised",
        bd=6,
        width=18,
        height=4,
        command=lambda: launch_level(2, child_name),
        cursor="hand2"
    )
    level2_btn.grid(row=0, column=1, padx=20, pady=15)
    
    # Level 3 Button
    level3_btn = tk.Button(
        buttons_frame,
        text="🔊 LEVEL 3\nAudio Matching",
        font=("Arial", 26, "bold"),
        bg="#e74c3c",
        fg="white",
        activebackground="#c0392b",
        activeforeground="white",
        relief="raised",
        bd=6,
        width=18,
        height=4,
        command=lambda: launch_level(3, child_name),
        cursor="hand2"
    )
    level3_btn.grid(row=1, column=0, padx=20, pady=15)
    
    # Progressive Mode Button
    progressive_btn = tk.Button(
        buttons_frame,
        text="🎯 PROGRESSIVE MODE\nLevel 1 → 2 → 3",
        font=("Arial", 26, "bold"),
        bg="#9b59b6",
        fg="white",
        activebackground="#8e44ad",
        activeforeground="white",
        relief="raised",
        bd=6,
        width=18,
        height=4,
        command=lambda: launch_level(1, child_name),
        cursor="hand2"
    )
    progressive_btn.grid(row=1, column=1, padx=20, pady=15)
    
    # Exit Button
    exit_btn = tk.Button(
        menu_container,
        text="EXIT",
        font=("Arial", 24, "bold"),
        bg="#95a5a6",
        fg="white",
        activebackground="#7f8c8d",
        activeforeground="white",
        relief="raised",
        bd=5,
        padx=30,
        pady=10,
        command=exit_app,
        cursor="hand2"
    )
    exit_btn.pack(pady=30)

# Start with name entry
show_name_entry()
root.mainloop()