import pygame
import serial
import time
import threading
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

# ========== CONFIG ========== #
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

BASE_DIR = "/home/pi/asd_learning_system"
IMAGE_PATH = os.path.join(BASE_DIR, "animal_images")
SOUND_PATH = os.path.join(BASE_DIR, "animal_sounds")
DEFAULT_IMAGE = os.path.join(IMAGE_PATH, "default_image.jpg")

# ========== RFID UID MAP ========== #
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

# ========== SERIAL INIT ========== #
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except serial.SerialException as e:
    print("Serial Error:", e)
    sys.exit()

pygame.init()
pygame.mixer.init()

# ========== GUI ROOT ========== #
root = tk.Tk()
root.title("Adaptive Learning System")
root.attributes("-fullscreen", True)
root.configure(bg="#f1faee")

current_level = None
child_name = ""

# ========== UTILITY FUNCTIONS ========== #

def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()

def play_sound(animal):
    try:
        sound_file = os.path.join(SOUND_PATH, f"{animal}_sound.mp3")
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
    except Exception as e:
        print("Audio error:", e)

# ========== LEVEL 1 LOGIC ========== #

def show_animal(animal):
    try:
        img_file = os.path.join(IMAGE_PATH, f"{animal}_image.jpg")
        img = Image.open(img_file).resize((800, 600))
        photo = ImageTk.PhotoImage(img)

        image_label.config(image=photo)
        image_label.image = photo
        name_label.config(text=animal.capitalize())

        threading.Thread(target=play_sound, args=(animal,), daemon=True).start()
    except Exception as e:
        print("Display error:", e)

def check_rfid():
    if current_level != 1:
        return

    if ser.in_waiting:
        uid = ser.readline().decode(errors="ignore").strip().upper()
        if uid in animal_data:
            show_animal(animal_data[uid])

    root.after(100, check_rfid)

# ========== LEVEL 1 SCREEN ========== #

def start_level_1():
    global current_level
    current_level = 1
    clear_screen()

    tk.Label(
        root,
        text=f"Level 1: Learning Mode\nHello {child_name}",
        font=("Arial", 28, "bold"),
        bg="#f1faee"
    ).pack(pady=20)

    global image_label, name_label

    default_img = Image.open(DEFAULT_IMAGE).resize((800, 600))
    default_photo = ImageTk.PhotoImage(default_img)

    image_label = tk.Label(root, image=default_photo, bg="#f1faee")
    image_label.image = default_photo
    image_label.pack()

    name_label = tk.Label(root, text="", font=("Arial", 24), bg="#f1faee")
    name_label.pack(pady=10)

    tk.Button(
        root,
        text="Back to Home",
        font=("Arial", 16),
        command=home_page
    ).pack(pady=20)

    check_rfid()

# ========== HOME PAGE ========== #

def home_page():
    global current_level
    current_level = None
    clear_screen()

    tk.Label(
        root,
        text="Welcome to Adaptive Learning System",
        font=("Arial", 32, "bold"),
        bg="#f1faee"
    ).pack(pady=30)

    tk.Label(
        root,
        text="Enter your name:",
        font=("Arial", 20),
        bg="#f1faee"
    ).pack(pady=10)

    name_entry = tk.Entry(root, font=("Arial", 20))
    name_entry.pack(pady=10)

    def submit_name():
        global child_name
        child_name = name_entry.get().strip()
        if child_name:
            level_selection()

    tk.Button(
        root,
        text="Start",
        font=("Arial", 18),
        command=submit_name
    ).pack(pady=20)

# ========== LEVEL SELECTION ========== #

def level_selection():
    clear_screen()

    tk.Label(
        root,
        text=f"Hello {child_name}, Choose a Level",
        font=("Arial", 28, "bold"),
        bg="#f1faee"
    ).pack(pady=30)

    tk.Button(
        root,
        text="Level 1: Learning",
        font=("Arial", 20),
        width=25,
        command=start_level_1
    ).pack(pady=10)

    tk.Button(
        root,
        text="Level 2: Image Matching (Coming Soon)",
        font=("Arial", 18),
        width=35,
        state="disabled"
    ).pack(pady=10)

    tk.Button(
        root,
        text="Level 3: Audio Matching (Coming Soon)",
        font=("Arial", 18),
        width=35,
        state="disabled"
    ).pack(pady=10)

# ========== START APP ========== #

home_page()
root.mainloop()
