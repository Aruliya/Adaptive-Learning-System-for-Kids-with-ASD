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
random.shuffle(animal_sequence)

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
accept_input = False
child_name = ""

# ---------- UI ----------
image_label = tk.Label(root, bg="#f1faee")
image_label.pack(expand=True)

status_label = tk.Label(root, font=("Arial", 28), bg="#f1faee")
status_label.pack(pady=20)

# ---------- AUDIO ----------
def play_audio_blocking(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        root.update()

def play_audio_non_blocking(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()

# ---------- GIF SYSTEM ----------
gif_cache = {}
gif_running = False
current_gif_id = 0

def preload_gifs():
    for gif in os.listdir(GIF_PATH):
        if gif.endswith(".gif"):
            path = os.path.join(GIF_PATH, gif)
            frames = [
                ImageTk.PhotoImage(
                    frame.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
                )
                for frame in ImageSequence.Iterator(Image.open(path))
            ]
            gif_cache[gif] = frames

def show_gif(gif_name, loop=True):
    global gif_running, current_gif_id, accept_input

    accept_input = False
    gif_running = False
    current_gif_id += 1
    gif_id = current_gif_id

    frames = gif_cache.get(gif_name)
    if not frames:
        return

    gif_running = True

    def animate(i=0):
        if not gif_running or gif_id != current_gif_id:
            return
        image_label.config(image=frames[i])
        next_i = i + 1 if i + 1 < len(frames) else (0 if loop else i)
        root.after(80, animate, next_i)

    animate()

def stop_gif():
    global gif_running
    gif_running = False
    image_label.config(image="")

# ---------- WARM-UP FIX ----------
def warm_up_display():
    first_gif = next(iter(gif_cache.values()))
    image_label.config(image=first_gif[0])
    root.update_idletasks()
    image_label.config(image="")

# ---------- GAME UTIL ----------
def set_accept_input():
    global accept_input
    accept_input = True

def show_current_animal():
    global accept_input
    accept_input = False

    img = Image.open(os.path.join(IMAGE_PATH, f"{current_animal}_image.jpg"))
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
    photo = ImageTk.PhotoImage(img)

    image_label.config(image=photo)
    image_label.image = photo

    root.after(200, set_accept_input)

# ---------- NAME SCREEN ----------
def name_screen():
    show_gif("default_level2.gif", loop=True)
    status_label.config(text="Enter Child Name")

    entry = tk.Entry(root, font=("Arial", 28))
    entry.pack(pady=20)

    def submit():
        global child_name
        child_name = entry.get().strip()
        entry.destroy()
        start_game()

    tk.Button(root, text="Start Level 2", font=("Arial", 20), command=submit).pack()

# ---------- GAME FLOW ----------
def start_game():
    stop_gif()
    show_next_animal()

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
    global retry_count, score

    if game_over or current_animal is None or not accept_input:
        root.after(300, check_rfid)
        return

    if ser.in_waiting:
        uid = ser.readline().decode(errors="ignore").strip().upper()

        # ✅ CORRECT TAP (UNCHANGED)
        if uid == animal_to_uid[current_animal]:
            score += 1
            play_audio_blocking(os.path.join(SOUND_PATH, f"{current_animal}_sound.mp3"))
            show_gif("goodJob.gif", loop=False)
            play_audio_non_blocking(os.path.join(SOUND_PATH, "correct_sound.mp3"))
            root.after(2000, show_next_animal)

        # ❌ WRONG TAP (FIXED)
        else:
            retry_count += 1

            if retry_count < MAX_RETRIES:
                stop_gif()
                show_gif("tryAgain.gif", loop=False)
                play_audio_non_blocking(os.path.join(SOUND_PATH, "incorrect_sound.mp3"))

                def return_to_image():
                    stop_gif()
                    show_current_animal()

                root.after(1200, return_to_image)

            else:
                stop_gif()
                show_gif("uhOh.gif", loop=False)
                play_audio_non_blocking(os.path.join(SOUND_PATH, "oops_sound.mp3"))
                root.after(1800, show_next_animal)

    root.after(300, check_rfid)

# ---------- END GAME ----------
def end_game():
    global game_over
    game_over = True

    stop_gif()
    show_gif("finalScore.gif", loop=True)

    status_label.config(
        text=f"{child_name}, you identified {score} / {TOTAL_QUESTIONS} correctly",
        font=("Arial", 36, "bold")
    )

# ---------- START ----------
preload_gifs()
warm_up_display()
name_screen()
check_rfid()
root.mainloop()
