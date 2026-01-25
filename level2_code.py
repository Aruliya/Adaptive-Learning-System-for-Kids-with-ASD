import pygame
import serial
import random
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

print("=== Level 2: Image Identification Mode Started ===")

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

BASE_DIR = "/home/pi/asd_learning_system"
IMAGE_PATH = os.path.join(BASE_DIR, "animal_images")
SOUND_PATH = os.path.join(BASE_DIR, "animal_sounds")

TOTAL_QUESTIONS = 10
MAX_RETRIES = 3

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

root = tk.Tk()
root.attributes("-fullscreen", True)
root.overrideredirect(True)
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
root.configure(bg="#f1faee")

current_animal = None
question_count = 0
retry_count = 0
score = 0

def play_audio_blocking(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        root.update()

def show_new_animal():
    global current_animal, retry_count, question_count

    if question_count >= TOTAL_QUESTIONS:
        show_result()
        return

    retry_count = 0
    current_animal = random.choice(animal_list)
    question_count += 1

    print(f"Question {question_count}: {current_animal}")

    img = Image.open(os.path.join(IMAGE_PATH, f"{current_animal}_image.jpg"))
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()-100))
    photo = ImageTk.PhotoImage(img)
    image_label.config(image=photo)
    image_label.image = photo
    status_label.config(text=f"Question {question_count}/10")

def check_rfid():
    global retry_count, score

    if ser.in_waiting:
        uid = ser.readline().decode(errors="ignore").strip().upper()
        print(f"RFID scanned: {uid}")

        if uid == animal_to_uid[current_animal]:
            score += 1
            status_label.config(text="Correct!", fg="green")
            play_audio_blocking(os.path.join(SOUND_PATH, "correct_sound.mp3"))
            play_audio_blocking(os.path.join(SOUND_PATH, f"{current_animal}_sound.mp3"))
            root.after(500, show_new_animal)
        else:
            retry_count += 1
            status_label.config(text="Try again", fg="red")
            play_audio_blocking(os.path.join(SOUND_PATH, "incorrect_sound.mp3"))
            if retry_count >= MAX_RETRIES:
                print("Max retries reached")
                root.after(500, show_new_animal)

    root.after(300, check_rfid)

def show_result():
    clear()
    result = f"You identified {score} / {TOTAL_QUESTIONS} correctly"
    print(result)
    tk.Label(root, text=result, font=("Arial", 36, "bold"), bg="#f1faee").pack(expand=True)

def clear():
    for w in root.winfo_children():
        w.destroy()

image_label = tk.Label(root, bg="#f1faee")
image_label.pack()

status_label = tk.Label(root, font=("Arial", 28), bg="#f1faee")
status_label.pack()

show_new_animal()
check_rfid()
root.mainloop()
