import pygame
import serial
import time
import random
import threading
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

print("=== Level 2: Visual Identification Mode Started ===")

# ========== CONFIG ==========
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

BASE_DIR = "/home/pi/asd_learning_system"

IMAGE_PATH = os.path.join(BASE_DIR, "animal_images")
SOUND_PATH = os.path.join(BASE_DIR, "animal_sounds")
DEFAULT_IMAGE = os.path.join(IMAGE_PATH, "default_image.jpg")

# ========== RFID MAP ==========
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

# ========== SERIAL INIT ==========
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Serial connection established")
except Exception as e:
    print("Serial error:", e)
    sys.exit()

pygame.init()
pygame.mixer.init()

# ========== GUI ==========
root = tk.Tk()
root.title("Level 2 - Image Identification")
root.attributes("-fullscreen", True)
root.configure(bg="#f1faee")

current_target = None

# ========== FUNCTIONS ==========

def play_sound(sound_file):
    try:
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
    except Exception as e:
        print("Audio error:", e)

def show_new_target():
    global current_target

    current_target = random.choice(list(animal_to_uid.keys()))
    print(f"Target animal displayed: {current_target}")

    img_path = os.path.join(IMAGE_PATH, f"{current_target}_image.jpg")
    img = Image.open(img_path).resize((800, 600))
    photo = ImageTk.PhotoImage(img)

    image_label.config(image=photo)
    image_label.image = photo
    status_label.config(text="Scan the matching card", fg="black")

def check_rfid():
    if ser.in_waiting:
        uid = ser.readline().decode(errors="ignore").strip().upper()
        print(f"RFID scanned: {uid}")

        if uid == animal_to_uid[current_target]:
            print("✅ Correct card scanned")
            status_label.config(text="Correct!", fg="green")
            play_sound(os.path.join(SOUND_PATH, f"{current_target}_sound.mp3"))
            root.after(2000, show_new_target)
        else:
            print("❌ Wrong card scanned")
            status_label.config(text="Wrong card, try again", fg="red")

    root.after(1000, check_rfid)

# ========== UI SETUP ==========

tk.Label(
    root,
    text="Level 2: Image Identification Mode",
    font=("Arial", 28, "bold"),
    bg="#f1faee"
).pack(pady=20)

default_img = Image.open(DEFAULT_IMAGE).resize((800, 600))
default_photo = ImageTk.PhotoImage(default_img)

image_label = tk.Label(root, image=default_photo, bg="#f1faee")
image_label.image = default_photo
image_label.pack()

status_label = tk.Label(
    root,
    text="Get Ready...",
    font=("Arial", 22),
    bg="#f1faee"
)
status_label.pack(pady=20)

print("Initializing Level 2...")
root.after(1000, show_new_target)
check_rfid()

root.mainloop()
