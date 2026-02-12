import pygame
import serial
import subprocess
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import time
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import datetime

print("=== Level 1: Learning Mode Started ===")

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

BASE_DIR = "/home/pi/asd_learning_system"
IMAGE_PATH = os.path.join(BASE_DIR, "animal_images")
SOUND_PATH = os.path.join(BASE_DIR, "animal_sounds")
DEFAULT_IMAGE = os.path.join(IMAGE_PATH, "default_image.jpg")
STATS_FILE = os.path.join(BASE_DIR, "level1_interaction_stats.xlsx")

# Get name from command line or default
child_name = sys.argv[1] if len(sys.argv) > 1 else "Player"
print(f"Level 1 started for: {child_name}")

# Tracking statistics
animal_tap_count = {}  # {animal_name: tap_count}
animal_time_total = {}  # {animal_name: total_time_spent}
current_animal = None  # Currently displayed animal
animal_start_time = None  # When current animal was shown

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
    # Finalize tracking for current animal
    global current_animal, animal_start_time
    if current_animal is not None and animal_start_time is not None:
        time_spent = time.time() - animal_start_time
        animal_time_total[current_animal] = animal_time_total.get(current_animal, 0) + time_spent
    
    pygame.mixer.music.stop()
    if ser.is_open:
        ser.close()
    root.destroy()
    # Return to launcher
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "main_launcher.py")])

def go_to_level2():
    """Save stats, show them, then progress to Level 2"""
    # Finalize tracking for current animal
    global current_animal, animal_start_time
    if current_animal is not None and animal_start_time is not None:
        time_spent = time.time() - animal_start_time
        animal_time_total[current_animal] = animal_time_total.get(current_animal, 0) + time_spent
    
    # Save stats to Excel
    save_stats()
    
    # Show stats screen
    show_stats_screen()

def save_stats():
    """Save interaction stats to Excel file"""
    try:
        if os.path.exists(STATS_FILE):
            wb = load_workbook(STATS_FILE)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = "Level 1 Stats"
            
            headers = ["Name", "Animal", "Tap Count", "Time Spent (s)", "Date", "Time"]
            ws.append(headers)
            
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=12)
            
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            ws.column_dimensions['A'].width = 20
            ws.column_dimensions['B'].width = 15
            ws.column_dimensions['C'].width = 12
            ws.column_dimensions['D'].width = 18
            ws.column_dimensions['E'].width = 15
            ws.column_dimensions['F'].width = 12
        
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        # Add a row for each animal explored
        for animal, tap_count in sorted(animal_tap_count.items()):
            time_spent = animal_time_total.get(animal, 0)
            new_row = [child_name, animal, tap_count, round(time_spent, 2), date_str, time_str]
            ws.append(new_row)
            
            row_num = ws.max_row
            for cell in ws[row_num]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
        
        wb.save(STATS_FILE)
        print(f"✓ Stats saved to {STATS_FILE}")
        return True
    except Exception as e:
        print(f"✗ Error saving stats: {e}")
        return False

def show_stats_screen():
    """Display interaction statistics before proceeding to Level 2"""
    global root
    
    root.after(1000)  # Brief delay
    
    # Clear previous widgets
    for widget in root.winfo_children():
        widget.pack_forget()
    
    # Stats container
    stats_frame = tk.Frame(root, bg="#F4FFDB")
    stats_frame.pack(expand=True, fill="both")
    
    # Title
    title = tk.Label(
        stats_frame,
        text="Level 1 Interaction Statistics",
        font=("Arial", 32, "bold"),
        bg="#F4FFDB",
        fg="#1d3557"
    )
    title.pack(pady=20)
    
    # Stats info
    total_taps = sum(animal_tap_count.values())
    total_time = sum(animal_time_total.values())
    unique_animals = len(animal_tap_count)
    
    info_text = f"Total Animals Explored: {unique_animals}\n"
    info_text += f"Total Taps: {total_taps}\n"
    info_text += f"Total Time: {total_time:.2f}s\n\n"
    info_text += "Animal Breakdown:\n"
    info_text += "-" * 40 + "\n"
    
    for animal in sorted(animal_tap_count.keys()):
        taps = animal_tap_count[animal]
        duration = animal_time_total.get(animal, 0)
        avg_time = duration / taps if taps > 0 else 0
        info_text += f"{animal.upper():12} | Taps: {taps:2} | Total: {duration:6.2f}s | Avg: {avg_time:5.2f}s\n"
    
    stats_label = tk.Label(
        stats_frame,
        text=info_text,
        font=("Arial", 16),
        bg="#F4FFDB",
        fg="#1d3557",
        justify="left"
    )
    stats_label.pack(pady=20, padx=20)
    
    # Continue button
    continue_btn = tk.Button(
        stats_frame,
        text="Continue to Level 2",
        font=("Arial", 24, "bold"),
        bg="#27ae60",
        fg="white",
        activebackground="#229954",
        activeforeground="white",
        relief="raised",
        padx=30,
        pady=15,
        command=lambda: proceed_to_level2(),
        cursor="hand2"
    )
    continue_btn.pack(pady=20)

def proceed_to_level2():
    """Proceed to Level 2 after stats are shown"""
    print(f"Progressing to Level 2 for {child_name}")
    pygame.mixer.music.stop()
    if ser.is_open:
        ser.close()
    root.destroy()
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "cv_level2_original.py"), child_name])

root = tk.Tk()
root.title("Level 1 - Learning Mode")
root.attributes("-fullscreen", True)
root.bind("<Escape>", exit_app)
root.bind("<Control-q>", exit_app)
root.overrideredirect(True)
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
root.configure(bg="#ffffff")
root.focus_force()

def play_sound(animal):
    sound_file = os.path.join(SOUND_PATH, f"{animal}_sound.mp3")
    try:
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(1.0)
    except:
        pass

def show_animal(animal):
    """Display animal image/sound and track interaction"""
    global current_animal, animal_start_time
    
    # If switching from a different animal, save time spent on previous one
    if current_animal is not None and current_animal != animal and animal_start_time is not None:
        time_spent = time.time() - animal_start_time
        animal_time_total[current_animal] = animal_time_total.get(current_animal, 0) + time_spent
        print(f"  {current_animal}: +{time_spent:.2f}s (total: {animal_time_total[current_animal]:.2f}s)")
    
    # Start tracking new animal
    current_animal = animal
    animal_start_time = time.time()
    
    # Increment tap count
    animal_tap_count[animal] = animal_tap_count.get(animal, 0) + 1
    
    print(f"Showing animal: {animal} (tap #{animal_tap_count[animal]})")
    
    try:
        img_path = os.path.join(IMAGE_PATH, f"{animal}_image.jpg")
        img = Image.open(img_path).resize(
            (root.winfo_screenwidth(), root.winfo_screenheight()-100)
        )
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo
        name_label.config(text=animal.upper())
        play_sound(animal)
    except Exception as e:
        print(f"Error showing animal: {e}")

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

image_label = tk.Label(root, image=default_photo, bg="#F4FFDB")
image_label.pack()

name_label = tk.Label(root, text="", font=("Arial", 40, "bold"), bg="#ffffff")
name_label.pack()

# Control buttons frame (top-right corner)
controls_frame = tk.Frame(root, bg="#FFFFFF")
controls_frame.place(relx=0.98, rely=0.02, anchor="ne")

# Next Level button
next_level_btn = tk.Button(
    controls_frame,
    text="Next Level",
    font=("Arial", 18, "bold"),
    bg="#27ae60",
    fg="white",
    activebackground="#229954",
    activeforeground="white",
    relief="raised",
    #bd=4,
    #padx=20,
    #pady=10,
    command=go_to_level2,
    cursor="hand2"
)
next_level_btn.pack(side="right", padx=5)

# Home button
home_btn = tk.Button(
    controls_frame,
    text="Home",
    font=("Arial", 18, "bold"),
    bg="#3498db",
    fg="white",
    activebackground="#2980b9",
    activeforeground="white",
    relief="raised",
    #bd=4,
    #padx=20,
    #pady=10,
    command=exit_app,
    cursor="hand2"
)
home_btn.pack(side="right", padx=5)

check_rfid()
root.mainloop()
