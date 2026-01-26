import pygame
import serial
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os
import sys
import random

print("=== Level 2: Image Identification Mode Started ===")

# ---------- CONFIG ----------
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

BASE_DIR = "/home/pi/asd_learning_system"
IMAGE_PATH = os.path.join(BASE_DIR, "animal_images")
SOUND_PATH = os.path.join(BASE_DIR, "animal_sounds")
GIF_PATH = os.path.join(BASE_DIR, "feedback_gifs")

TOTAL_QUESTIONS = 14
MAX_RETRIES = 3

# ---------- RFID MAP ----------
animal_data = {
    "936FA320": "cat", "33719E20": "horse", "6371A320": "elephant",
    "C376B420": "lion", "536E4BE4": "parrot", "33A8B920": "dog",
    "339FFC30": "sheep", "03548F22": "donkey", "131CF430": "monkey",
    "236A8222": "duck", "135C7A31": "crow", "73C28131": "cow",
    "E3257622": "dolphin", "23EB9022": "frog", "033D9423": "chicken"
}

animal_to_uid = {v: k for k, v in animal_data.items()}
animal_sequence = list(animal_to_uid.keys())
random.shuffle(animal_sequence)  # no repetition

# ---------- SERIAL ----------
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except:
    print("Serial error")
    sys.exit()

# ---------- INIT ----------
pygame.init()
pygame.mixer.init()

root = tk.Tk()
root.attributes("-fullscreen", True)
root.overrideredirect(True)
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
root.configure(bg="#f1faee")
root.focus_force()

# ---------- EXIT ----------
def exit_app(event=None):
    pygame.mixer.music.stop()
    if ser.is_open:
        ser.close()
    root.destroy()

root.bind("<Escape>", exit_app)
root.bind("<Control-q>", exit_app)

# ---------- STATE ----------
current_animal = None
question_index = 0
retry_count = 0
score = 0
game_over = False
gif_running = False
child_name = ""
accept_input = True


# ---------- UI ----------
image_label = tk.Label(root, bg="#f1faee")
image_label.pack(expand=True)

status_label = tk.Label(root, font=("Arial", 28), bg="#f1faee")
status_label.pack(pady=20)

# ---------- UTILITIES ----------
def play_audio_blocking(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        root.update()

def play_audio_non_blocking(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()

def show_gif(gif_name):
    global accept_input
    accept_input = False

    global gif_running
    gif_running = False
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

def stop_gif():
    global gif_running
    gif_running = False
    image_label.config(image="")

def show_current_animal():
    global accept_input
    accept_input = False
    img = Image.open(os.path.join(IMAGE_PATH, f"{current_animal}_image.jpg"))
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
    photo = ImageTk.PhotoImage(img)
    image_label.config(image=photo)
    image_label.image = photo
    root.after(300, lambda: set_accept_input())

def set_accept_input():
    global accept_input
    accept_input = True

# ---------- NAME SCREEN ----------
def name_screen():
    image_label.config(image="")
    status_label.config(text="Enter Child Name")

    entry = tk.Entry(root, font=("Arial", 28))
    entry.pack(pady=20)

    def submit():
        nonlocal entry
        global child_name
        child_name = entry.get().strip()
        entry.destroy()
        start_game()

    tk.Button(root, text="Start Level 2", font=("Arial", 20), command=submit).pack()

# ---------- GAME FLOW ----------
def start_game():
    show_gif("default_level2.gif")  # no delay
    root.after(500, show_next_animal)

def show_next_animal():
    global current_animal, retry_count, question_index

    stop_gif()

    if question_index >= TOTAL_QUESTIONS:
        end_game()
        return

    retry_count = 0
    current_animal = animal_sequence[question_index]
    question_index += 1

    show_current_animal()
    status_label.config(text=f"{child_name}  |  {question_index}/{TOTAL_QUESTIONS}")

def check_rfid():
    global retry_count, score, game_over, accept_input

    if game_over or current_animal is None or not accept_input:
        root.after(300, check_rfid)
        return

    if ser.in_waiting:
        uid = ser.readline().decode(errors="ignore").strip().upper()

        if uid == animal_to_uid[current_animal]:
            score += 1

            # 1️⃣ animal sound first
            play_audio_blocking(os.path.join(SOUND_PATH, f"{current_animal}_sound.mp3"))

            # 2️⃣ feedback GIF + correct sound together
            show_gif("goodJob.gif")
            play_audio_non_blocking(os.path.join(SOUND_PATH, "correct_sound.mp3"))

            root.after(2000, show_next_animal)

        else:
            retry_count += 1

            if retry_count < MAX_RETRIES:
                show_gif("tryAgain.gif")
                play_audio_non_blocking(os.path.join(SOUND_PATH, "incorrect_sound.mp3"))
                root.after(1500, show_current_animal)
            else:
                show_gif("uhOh.gif")
                play_audio_non_blocking(os.path.join(SOUND_PATH, "oops_sound.mp3"))
                root.after(2000, show_next_animal)

    root.after(300, check_rfid)

def end_game():
    global game_over
    game_over = True

    stop_gif()           # ← ADD THIS
    image_label.config(image="")
    show_gif("finalScore.gif")

    status_label.config(
        text=f"{child_name}, you identified {score} / {TOTAL_QUESTIONS} correctly",
        font=("Arial", 36, "bold")
    )


# ---------- START ----------
name_screen()
check_rfid()
root.mainloop()
