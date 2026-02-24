# pink color #F4FFDB
# orange color #F6AE5B

import pygame
import serial
import subprocess
import sys
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os

print("=== ASD Learning System Launcher ===")
BASE_DIR = "/home/pi/asd_learning_system"
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GIF_PATH = os.path.join(BASE_DIR, "feedback_gifs")

pygame.init()
pygame.mixer.init()

root = tk.Tk()
root.title("ASD Learning System")
root.attributes("-fullscreen", True)
root.overrideredirect(True)
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
root.configure(bg="#F4FFDB")
root.focus_force()

child_name = ""

def exit_app(event=None):
    print("Exiting launcher...")
    root.destroy()
    sys.exit()

root.bind("<Escape>", exit_app)
root.bind("<Control-q>", exit_app)

# Main container
main_frame = tk.Frame(root, bg="#F4FFDB")
main_frame.pack(expand=True, fill="both")

def launch_level(level_num, name):
    """Launch a specific level with the child's name"""
    print(f"Launching Level {level_num} for {name}")
    root.destroy()

    # Pass name as command line argument
    if level_num == 0:
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "a_level0_code.py"), name])
    elif level_num == 1:
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "a_level1_code.py"), name])
    elif level_num == 2:
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "cv_level2.py"), name])
    elif level_num == 3:
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "level3_code.py"), name])


def launch_progressive(name):
    """Start progressive mode: run level 0 then let levels chain using each level's logic."""
    print(f"Launching Progressive Mode starting Level 0 for {name}")
    root.destroy()
    # Start at Level 0 which should chain to Level 1 (the level scripts are responsible
    # for launching the next level and passing along the name).
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "a_level0_code.py"), name])


def ask_name_and_launch(level_num=None, progressive=False):
    """Prompt for a name, then launch the chosen level or progressive mode.

    If progressive=True, `level_num` is ignored and `launch_progressive` is used.
    """
    prompt = tk.Toplevel(root)
    prompt.title("Enter Name")
    prompt.geometry("400x200")
    prompt.attributes("-topmost", True)
    prompt.transient(root)
    prompt.grab_set()

    lbl = tk.Label(prompt, text="Enter name to start:", font=("Arial", 16))
    lbl.pack(pady=12)
    entry = tk.Entry(prompt, font=("Arial", 16), justify='center')
    entry.pack(pady=8)
    entry.focus()

    def on_submit():
        name = entry.get().strip() or "Player"
        prompt.grab_release()
        prompt.destroy()
        # Give the window a moment to close before destroying root
        root.after(100, lambda: execute_launch(name, level_num, progressive))

    def execute_launch(name, level_num, progressive):
        if progressive:
            launch_progressive(name)
        else:
            launch_level(level_num, name)

    submit_btn = tk.Button(prompt, text="START", font=("Arial", 14, "bold"), command=on_submit)
    submit_btn.pack(pady=10)
    
    entry.bind("<Return>", lambda e: on_submit())

def show_name_entry():
    """Show name entry screen"""
    for widget in main_frame.winfo_children():
        widget.destroy()
    
    entry_container = tk.Frame(main_frame, bg="#F4FFDB")
    entry_container.pack(expand=True)
    
    # Welcome GIF
    gif_label = tk.Label(entry_container, bg="#F4FFDB")
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
        text="Welcome to Animal Learning",
        font=("Arial", 44, "bold"),
        bg="#F4FFDB",
        fg="#2c3e50"
    )
    title.pack(pady=20)
    
    # Name entry
    name_label = tk.Label(
        entry_container,
        text="What's your name?",
        font=("Arial", 32, "bold"),
        bg="#F4FFDB",
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
    
    menu_container = tk.Frame(main_frame, bg="#F4FFDB")
    menu_container.pack(expand=True)
    
    # Welcome message
    welcome = tk.Label(
        menu_container,
        text=f"Hello, {child_name}!",
        font=("Arial", 42, "bold"),
        bg="#F4FFDB",
        fg="#2c3e50"
    )
    welcome.pack(pady=30)
    
    instruction = tk.Label(
        menu_container,
        text="Choose Your Learning Level",
        font=("Arial", 32),
        bg="#F4FFDB",
        fg="#34495e"
    )
    instruction.pack(pady=10)
    
    # Level buttons container
    buttons_frame = tk.Frame(menu_container, bg="#F4FFDB")
    buttons_frame.pack(pady=40)
    
    # Level 0 Button
    level0_btn = tk.Button(
        buttons_frame,
        text="LEVEL 0\nContinuous Learning",
        font=("Arial", 26, "bold"),
        bg="#16a085",
        fg="white",
        activebackground="#138d75",
        activeforeground="white",
        relief="raised",
        bd=6,
        width=18,
        height=4,
        command=lambda: ask_name_and_launch(level_num=0, progressive=False),
        cursor="hand2"
    )
    level0_btn.grid(row=0, column=0, padx=20, pady=15)

    # Level 1 Button
    level1_btn = tk.Button(
        buttons_frame,
        text="LEVEL 1\nFree Learning",
        font=("Arial", 26, "bold"),
        bg="#27ae60",
        fg="white",
        activebackground="#229954",
        activeforeground="white",
        relief="raised",
        bd=6,
        width=18,
        height=4,
        command=lambda: ask_name_and_launch(level_num=1, progressive=False),
        cursor="hand2"
    )
    level1_btn.grid(row=0, column=1, padx=20, pady=15)
    
    # Level 2 Button
    level2_btn = tk.Button(
        buttons_frame,
        text="LEVEL 2\nImage Matching",
        font=("Arial", 26, "bold"),
        bg="#3498db",
        fg="white",
        activebackground="#2980b9",
        activeforeground="white",
        relief="raised",
        bd=6,
        width=18,
        height=4,
        command=lambda: ask_name_and_launch(level_num=2, progressive=False),
        cursor="hand2"
    )
    level2_btn.grid(row=1, column=0, padx=20, pady=15)
    
    # Level 3 Button
    level3_btn = tk.Button(
        buttons_frame,
        text="LEVEL 3\nAudio Matching",
        font=("Arial", 26, "bold"),
        bg="#e74c3c",
        fg="white",
        activebackground="#c0392b",
        activeforeground="white",
        relief="raised",
        bd=6,
        width=18,
        height=4,
        command=lambda: ask_name_and_launch(level_num=3, progressive=False),
        cursor="hand2"
    )
    level3_btn.grid(row=1, column=1, padx=20, pady=15)
    
    # Progressive Mode Button
    progressive_btn = tk.Button(
        buttons_frame,
        text="PROGRESSIVE MODE\nLevel 0 → 1 → 2 → 3",
        font=("Arial", 26, "bold"),
        bg="#9b59b6",
        fg="white",
        activebackground="#8e44ad",
        activeforeground="white",
        relief="raised",
        bd=6,
        width=18,
        height=4,
        command=lambda: ask_name_and_launch(progressive=True),
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

# Start with level menu (name will be requested per-mode when needed)
show_level_menu()
root.mainloop()
