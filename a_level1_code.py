import pygame
import serial
import subprocess
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

print("=== Level 1: Learning Mode Started ===")

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

BASE_DIR = "/home/pi/asd_learning_system"
IMAGE_PATH = os.path.join(BASE_DIR, "animal_images")
SOUND_PATH = os.path.join(BASE_DIR, "animal_sounds")
DEFAULT_IMAGE = os.path.join(IMAGE_PATH, "default_image.jpg")

# Get name from command line or default
child_name = sys.argv[1] if len(sys.argv) > 1 else "Player"
print(f"Level 1 started for: {child_name}")

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

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Serial connected")
except:
    print("Serial error")
    sys.exit()

pygame.init()
pygame.mixer.init()

def exit_app(event=None):
    print("Exiting Level 1...")
    pygame.mixer.music.stop()
    if ser.is_open:
        ser.close()
    root.destroy()
    # Return to launcher
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "launcher.py")])

def go_to_level2():
    """Progress to Level 2"""
    print(f"Progressing to Level 2 for {child_name}")
    pygame.mixer.music.stop()
    if ser.is_open:
        ser.close()
    root.destroy()
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "level2_enhanced.py"), child_name])

root = tk.Tk()
root.title("Level 1 - Learning Mode")
root.attributes("-fullscreen", True)
root.bind("<Escape>", exit_app)
root.bind("<Control-q>", exit_app)
root.overrideredirect(True)
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
root.configure(bg="#f1faee")
root.focus_force()

def play_sound(animal):
    sound_file = os.path.join(SOUND_PATH, f"{animal}_sound.mp3")
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(1.0)

def show_animal(animal):
    print(f"Showing animal: {animal}")
    img_path = os.path.join(IMAGE_PATH, f"{animal}_image.jpg")
    img = Image.open(img_path).resize(
        (root.winfo_screenwidth(), root.winfo_screenheight()-100)
    )
    photo = ImageTk.PhotoImage(img)
    image_label.config(image=photo)
    image_label.image = photo
    name_label.config(text=animal.upper())
    play_sound(animal)

def check_rfid():
    if ser.in_waiting:
        uid = ser.readline().decode(errors="ignore").strip().upper()
        print(f"RFID scanned: {uid}")
        if uid in animal_data:
            show_animal(animal_data[uid])
    root.after(500, check_rfid)

# Default image
default_img = Image.open(DEFAULT_IMAGE).resize(
    (root.winfo_screenwidth(), root.winfo_screenheight()-100)
)
default_photo = ImageTk.PhotoImage(default_img)

image_label = tk.Label(root, image=default_photo, bg="#f1faee")
image_label.pack()

name_label = tk.Label(root, text="", font=("Arial", 40, "bold"), bg="#f1faee")
name_label.pack()

# Control buttons frame (top-right corner)
controls_frame = tk.Frame(root, bg="#f1faee")
controls_frame.place(relx=0.98, rely=0.02, anchor="ne")

# Next Level button
next_level_btn = tk.Button(
    controls_frame,
    text="➡️ Next Level",
    font=("Arial", 18, "bold"),
    bg="#27ae60",
    fg="white",
    activebackground="#229954",
    activeforeground="white",
    relief="raised",
    bd=4,
    padx=20,
    pady=10,
    command=go_to_level2,
    cursor="hand2"
)
next_level_btn.pack(side="right", padx=5)

# Home button
home_btn = tk.Button(
    controls_frame,
    text="🏠 Home",
    font=("Arial", 18, "bold"),
    bg="#3498db",
    fg="white",
    activebackground="#2980b9",
    activeforeground="white",
    relief="raised",
    bd=4,
    padx=20,
    pady=10,
    command=exit_app,
    cursor="hand2"
)
home_btn.pack(side="right", padx=5)

check_rfid()
root.mainloop()