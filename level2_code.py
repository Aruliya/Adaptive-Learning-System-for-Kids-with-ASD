import pygame
import serial
import random
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os
import sys
import threading

print("=== Level 2: Image Identification Mode Started ===")

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

BASE_DIR = "/home/pi/asd_learning_system"
IMAGE_PATH = os.path.join(BASE_DIR, "animal_images")
SOUND_PATH = os.path.join(BASE_DIR, "animal_sounds")
GIF_PATH = os.path.join(BASE_DIR, "feedback_gifs")

TOTAL_QUESTIONS = 14
MAX_RETRIES = 3
gif_running = False
current_gif_frames = []

animal_data = {
    "936FA320": "cat",
    "33719E20": "horse",
    "6371A320": "elephant",
    "C376B420": "lion",
    "536E4BE4": "parrot",
    "33A8B920": "dog",
    "339FFC30": "sheep",
    "03548F22": "donkey",
    "131CF430": "monkey",
    "236A8222": "duck",
    "135C7A31": "crow",
    "73C28131": "cow",
    "E3257622": "dolphin",
    "23EB9022": "frog",
    "033D9423": "chicken"
}

animal_to_uid = {v: k for k, v in animal_data.items()}
animal_list = list(animal_to_uid.keys())

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except:
    print("Serial error")
    sys.exit()

pygame.init()
pygame.mixer.init()

def exit_app(event=None):
    print("Exiting application safely...")
    pygame.mixer.music.stop()
    if ser.is_open:
        ser.close()
    root.destroy()

root = tk.Tk()
root.attributes("-fullscreen", True)
root.bind("<Escape>", exit_app)
root.bind("<Control-q>", exit_app)
root.overrideredirect(True)
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
root.configure(bg="#f1faee")
root.focus_force()

current_animal = None
question_count = 0
retry_count = 0
score = 0
child_name = ""

# Main container
main_frame = tk.Frame(root, bg="#f1faee")
main_frame.pack(expand=True, fill="both")

image_label = tk.Label(main_frame, bg="#f1faee")
image_label.pack(expand=True)

status_label = tk.Label(main_frame, font=("Arial", 28), bg="#f1faee")
status_label.pack()

# ---------- UTILITIES ----------

def play_audio_non_blocking(file):
    """Play audio in a separate thread"""
    def play():
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
    threading.Thread(target=play, daemon=True).start()

def play_audio_blocking(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        root.update()

def show_current_animal():
    img = Image.open(os.path.join(IMAGE_PATH, f"{current_animal}_image.jpg"))
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
    photo = ImageTk.PhotoImage(img)
    image_label.config(image=photo)
    image_label.image = photo

def show_gif_with_audio(gif_name, audio_file=None, duration=2000, loop=False):
    """Show GIF and play audio simultaneously"""
    global gif_running, current_gif_frames
    gif_running = False
    root.update()
    gif_running = True

    # Load and resize GIF frames
    gif_path = os.path.join(GIF_PATH, gif_name)
    gif_image = Image.open(gif_path)
    current_gif_frames = [
        ImageTk.PhotoImage(frame.resize(
            (root.winfo_screenwidth(), root.winfo_screenheight())))
        for frame in ImageSequence.Iterator(gif_image)
    ]

    # Play audio if provided (non-blocking)
    if audio_file:
        play_audio_non_blocking(audio_file)

    def animate(idx=0, start_time=None):
        if start_time is None:
            start_time = root.after_idle(lambda: None)
        
        if not gif_running:
            return
        
        if not loop and idx >= len(current_gif_frames):
            # GIF played once, show last frame
            image_label.config(image=current_gif_frames[-1])
            return
            
        image_label.config(image=current_gif_frames[idx % len(current_gif_frames)])
        root.after(100, animate, (idx + 1), start_time)

    animate()
    
    if not loop:
        root.after(duration, stop_gif)

def stop_gif():
    global gif_running
    gif_running = False

# ---------- START SCREEN ----------

def show_start_screen():
    """Display welcome screen with GIF, name entry, and start button"""
    global child_name
    
    # Clear main frame
    for widget in main_frame.winfo_children():
        widget.pack_forget()
    
    # Create start screen container
    start_container = tk.Frame(main_frame, bg="#f1faee")
    start_container.pack(expand=True)
    
    # GIF label at top
    gif_label = tk.Label(start_container, bg="#f1faee")
    gif_label.pack(pady=20)
    
    # Load and play GIF once
    gif_path = os.path.join(GIF_PATH, "default_level2.gif")
    gif_image = Image.open(gif_path)
    gif_frames = [
        ImageTk.PhotoImage(frame.resize((600, 400)))
        for frame in ImageSequence.Iterator(gif_image)
    ]
    
    def animate_start_gif(idx=0):
        if idx < len(gif_frames):
            gif_label.config(image=gif_frames[idx])
            gif_label.image = gif_frames[idx]
            root.after(100, animate_start_gif, idx + 1)
        else:
            # Keep last frame displayed
            gif_label.config(image=gif_frames[-1])
            gif_label.image = gif_frames[-1]
    
    animate_start_gif()
    
    # Name entry section
    name_frame = tk.Frame(start_container, bg="#f1faee")
    name_frame.pack(pady=30)
    
    name_label = tk.Label(
        name_frame, 
        text="Enter Your Name:", 
        font=("Arial", 32, "bold"),
        bg="#f1faee",
        fg="#1d3557"
    )
    name_label.pack(pady=10)
    
    name_entry = tk.Entry(
        name_frame,
        font=("Arial", 28),
        width=20,
        justify="center",
        bg="white",
        fg="#1d3557",
        relief="solid",
        bd=2
    )
    name_entry.pack(pady=10)
    name_entry.focus()
    
    def start_game_clicked():
        global child_name
        child_name = name_entry.get().strip()
        if not child_name:
            child_name = "Player"
        print(f"Starting game for: {child_name}")
        start_container.destroy()
        start_game()
    
    # Bind Enter key
    name_entry.bind("<Return>", lambda e: start_game_clicked())
    
    # Start button
    start_btn = tk.Button(
        name_frame,
        text="START",
        font=("Arial", 32, "bold"),
        bg="#457b9d",
        fg="white",
        activebackground="#1d3557",
        activeforeground="white",
        relief="raised",
        bd=5,
        padx=40,
        pady=15,
        command=start_game_clicked,
        cursor="hand2"
    )
    start_btn.pack(pady=20)

# ---------- GAME FLOW ----------

def start_game():
    # Restore game widgets
    image_label.pack(expand=True)
    status_label.pack()
    
    # Show initial GIF briefly
    show_gif_with_audio("default_level2.gif", duration=2000, loop=True)
    root.after(2000, show_new_animal)

def show_new_animal():
    global current_animal, retry_count, question_count

    if question_count >= TOTAL_QUESTIONS:
        show_final_score()
        return

    stop_gif()
    retry_count = 0
    current_animal = random.choice(animal_list)
    question_count += 1

    print(f"Question {question_count}: {current_animal}")

    img = Image.open(os.path.join(IMAGE_PATH, f"{current_animal}_image.jpg"))
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
    photo = ImageTk.PhotoImage(img)
    image_label.config(image=photo)
    image_label.image = photo
    status_label.config(text=f"Question {question_count}/{TOTAL_QUESTIONS}", fg="#1d3557")

def check_rfid():
    global retry_count, score

    if current_animal is None:
        root.after(300, check_rfid)
        return

    if ser.in_waiting:
        uid = ser.readline().decode(errors="ignore").strip().upper()
        print(f"RFID scanned: {uid}")

        if uid == animal_to_uid[current_animal]:
            score += 1
            # Play animal sound first
            play_audio_blocking(os.path.join(SOUND_PATH, f"{current_animal}_sound.mp3"))
            # Then show GIF with correct sound simultaneously
            show_gif_with_audio(
                "goodJob.gif",
                os.path.join(SOUND_PATH, "correct_sound.mp3"),
                duration=2000
            )
            root.after(2000, show_new_animal)

        else:
            retry_count += 1
            if retry_count < MAX_RETRIES:
                # GIF and sound together
                show_gif_with_audio(
                    "tryAgain.gif",
                    os.path.join(SOUND_PATH, "incorrect_sound.mp3"),
                    duration=1500
                )
                root.after(1500, show_current_animal)
            else:
                # GIF and sound together
                show_gif_with_audio(
                    "uhOh.gif",
                    os.path.join(SOUND_PATH, "oops_sound.mp3"),
                    duration=2000
                )
                root.after(2000, show_new_animal)

    root.after(300, check_rfid)

def show_final_score():
    """Display final score with GIF playing once"""
    global gif_running, current_gif_frames
    
    stop_gif()
    status_label.pack_forget()
    
    # Create final screen container
    final_container = tk.Frame(main_frame, bg="#f1faee")
    final_container.pack(expand=True)
    
    # GIF label
    final_gif_label = tk.Label(final_container, bg="#f1faee")
    final_gif_label.pack(pady=20)
    
    # Score label
    score_text = f"Great Job, {child_name}!\n\nYou identified {score} out of {TOTAL_QUESTIONS} animals correctly!"
    score_label = tk.Label(
        final_container,
        text=score_text,
        font=("Arial", 36, "bold"),
        bg="#f1faee",
        fg="#1d3557",
        justify="center"
    )
    score_label.pack(pady=30)
    
    # Load and play final GIF once
    gif_path = os.path.join(GIF_PATH, "finalScore.gif")
    gif_image = Image.open(gif_path)
    final_frames = [
        ImageTk.PhotoImage(frame.resize((600, 400)))
        for frame in ImageSequence.Iterator(gif_image)
    ]
    
    def animate_final_gif(idx=0):
        if idx < len(final_frames):
            final_gif_label.config(image=final_frames[idx])
            final_gif_label.image = final_frames[idx]
            root.after(100, animate_final_gif, idx + 1)
        else:
            # Keep last frame displayed
            final_gif_label.config(image=final_frames[-1])
            final_gif_label.image = final_frames[-1]
    
    animate_final_gif()
    
    # Exit button
    exit_btn = tk.Button(
        final_container,
        text="EXIT",
        font=("Arial", 28, "bold"),
        bg="#e63946",
        fg="white",
        activebackground="#d62828",
        activeforeground="white",
        relief="raised",
        bd=5,
        padx=30,
        pady=10,
        command=exit_app,
        cursor="hand2"
    )
    exit_btn.pack(pady=20)

# ---------- START ----------
show_start_screen()
check_rfid()
root.mainloop()