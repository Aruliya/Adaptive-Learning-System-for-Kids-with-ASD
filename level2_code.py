import pygame
import serial
import random
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os
import sys

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

image_label = tk.Label(root, bg="#f1faee")
image_label.pack(expand=True)

status_label = tk.Label(root, font=("Arial", 28), bg="#f1faee")
status_label.pack()

# ---------- UTILITIES ----------

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


def show_gif(gif_name, duration=2000):
    global gif_running
    gif_running = False  # stop previous GIF
    gif_running = True

    frames = [
        ImageTk.PhotoImage(frame.resize(
            (root.winfo_screenwidth(), root.winfo_screenheight())))
        for frame in ImageSequence.Iterator(
            Image.open(os.path.join(GIF_PATH, gif_name)))
    ]

    def animate(idx=0):
        if not gif_running:
            return
        image_label.config(image=frames[idx])
        root.after(100, animate, (idx + 1) % len(frames))

    animate()
    root.after(duration, stop_gif)

def stop_gif():
    global gif_running
    gif_running = False
    image_label.config(image="")
    if current_animal is not None:
        show_current_animal()




# ---------- GAME FLOW ----------

def start_game():
    show_gif("default_level2.gif", 2000)
    root.after(2000, show_new_animal)

def show_new_animal():
    global current_animal, retry_count, question_count

    if question_count >= TOTAL_QUESTIONS:
        show_final_score()
        return

    retry_count = 0
    current_animal = random.choice(animal_list)
    question_count += 1

    print(f"Question {question_count}: {current_animal}")

    img = Image.open(os.path.join(IMAGE_PATH, f"{current_animal}_image.jpg"))
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
    photo = ImageTk.PhotoImage(img)
    image_label.config(image=photo)
    image_label.image = photo
    status_label.config(text=f"{question_count}/{TOTAL_QUESTIONS}")

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
            play_audio_blocking(os.path.join(SOUND_PATH, f"{current_animal}_sound.mp3"))
            play_audio_blocking(os.path.join(SOUND_PATH, "correct_sound.mp3"))
            show_gif("goodJob.gif", 2000)
            root.after(2000, show_new_animal)

        else:
            retry_count += 1
            if retry_count < MAX_RETRIES:
                play_audio_blocking(os.path.join(SOUND_PATH, "incorrect_sound.mp3"))
                show_gif("tryAgain.gif", 1500)
                root.after(1500, show_current_animal)  # ✅ SAME animal
            else:
                play_audio_blocking(os.path.join(SOUND_PATH, "oops_sound.mp3"))
                show_gif("uhOh.gif", 2000)
                root.after(2000, show_new_animal)

    root.after(300, check_rfid)


def show_final_score():
    image_label.config(image="")
    show_gif("finalScore.gif", 3000)
    status_label.config(
        text=f"You identified {score} / {TOTAL_QUESTIONS} correctly",
        font=("Arial", 36, "bold")
    )

# ---------- START ----------
start_game()
check_rfid()
root.mainloop()
