import pygame
import serial
import random
import subprocess
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os
import sys
import threading
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, PatternFill

print("=== Level 3: Audio Matching Mode Started ===")

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

BASE_DIR = "/home/pi/asd_learning_system"
IMAGE_PATH = os.path.join(BASE_DIR, "animal_images")
SOUND_PATH = os.path.join(BASE_DIR, "animal_sounds")
GIF_PATH = os.path.join(BASE_DIR, "feedback_gifs")
RESULTS_FILE = os.path.join(BASE_DIR, "level3_results.xlsx")

TOTAL_QUESTIONS = 14
MAX_RETRIES = 3
gif_running = False
current_gif_frames = []
accepting_input = False

# Get name from command line or show entry screen
child_name = sys.argv[1] if len(sys.argv) > 1 else ""

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

def go_home():
    """Return to launcher"""
    print("Returning to home...")
    pygame.mixer.music.stop()
    if ser.is_open:
        ser.close()
    root.destroy()
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "launcher.py")])

def exit_app(event=None):
    print("Exiting application safely...")
    global accepting_input
    accepting_input = False
    pygame.mixer.music.stop()
    if ser.is_open:
        ser.close()
    root.quit()
    root.destroy()

root = tk.Tk()
root.attributes("-fullscreen", True)
root.bind("<Escape>", exit_app)
root.bind("<Control-q>", exit_app)
root.overrideredirect(True)
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
root.configure(bg="#e0f7fa")
root.focus_force()

current_animal = None
question_count = 0
retry_count = 0
score = 0

# Main container
main_frame = tk.Frame(root, bg="#e0f7fa")
main_frame.pack(expand=True, fill="both")

image_label = tk.Label(main_frame, bg="#e0f7fa")
image_label.pack(expand=True)

status_label = tk.Label(main_frame, font=("Arial", 28), bg="#e0f7fa")
status_label.pack()

# ---------- UTILITIES ----------

def save_results_to_excel():
    """Save the game results to Excel file"""
    try:
        if os.path.exists(RESULTS_FILE):
            wb = load_workbook(RESULTS_FILE)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = "Level 3 Results"
            
            headers = ["Name", "Score", "Total Questions", "Percentage", "Date", "Time"]
            ws.append(headers)
            
            header_fill = PatternFill(start_color="00ACC1", end_color="00ACC1", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=12)
            
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            ws.column_dimensions['A'].width = 20
            ws.column_dimensions['B'].width = 10
            ws.column_dimensions['C'].width = 15
            ws.column_dimensions['D'].width = 12
            ws.column_dimensions['E'].width = 15
            ws.column_dimensions['F'].width = 12
        
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        percentage = round((score / TOTAL_QUESTIONS) * 100, 1)
        
        new_row = [child_name, score, TOTAL_QUESTIONS, f"{percentage}%", date_str, time_str]
        ws.append(new_row)
        
        row_num = ws.max_row
        for cell in ws[row_num]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        wb.save(RESULTS_FILE)
        print(f"Results saved: {child_name} - {score}/{TOTAL_QUESTIONS} ({percentage}%) - {date_str} {time_str}")
        return True
    except Exception as e:
        print(f"Error saving results: {e}")
        return False

def play_audio_non_blocking(file):
    """Play audio in a separate thread"""
    def play():
        try:
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()
        except:
            pass
    threading.Thread(target=play, daemon=True).start()

def play_audio_blocking(file):
    try:
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            root.update()
    except:
        pass

def play_animal_sound():
    """Play the current animal sound"""
    if current_animal:
        try:
            sound_file = os.path.join(SOUND_PATH, f"{current_animal}_sound.mp3")
            play_audio_blocking(sound_file)
        except Exception as e:
            print(f"Error playing sound: {e}")

def show_listening_screen():
    """Show a visual indicator that audio is playing"""
    try:
        # Clear any existing image
        image_label.config(image="")
        image_label.image = None
        
        # Create text display
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        
        # Create a frame for centered content
        listen_frame = tk.Frame(image_label, bg="#e0f7fa")
        listen_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        speaker_label = tk.Label(
            listen_frame,
            text="🔊",
            font=("Arial", 200),
            bg="#e0f7fa",
            fg="#00838f"
        )
        speaker_label.pack()
        
        instruction_label = tk.Label(
            listen_frame,
            text="Listen Carefully!",
            font=("Arial", 48, "bold"),
            bg="#e0f7fa",
            fg="#006064"
        )
        instruction_label.pack(pady=20)
        
        hint_label = tk.Label(
            listen_frame,
            text="Tap the matching card",
            font=("Arial", 32),
            bg="#e0f7fa",
            fg="#00838f"
        )
        hint_label.pack()
        
        # Store reference to prevent garbage collection
        image_label.listen_frame = listen_frame
        
    except Exception as e:
        print(f"Error showing listening screen: {e}")

def clear_listening_screen():
    """Clear the listening screen widgets"""
    try:
        if hasattr(image_label, 'listen_frame'):
            image_label.listen_frame.destroy()
            delattr(image_label, 'listen_frame')
    except:
        pass

def show_animal_with_name():
    """Show the animal image with its name"""
    try:
        clear_listening_screen()
        
        img = Image.open(os.path.join(IMAGE_PATH, f"{current_animal}_image.jpg"))
        img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight() - 150))
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo
        
        # Update status to show animal name
        status_label.config(
            text=f"✓ {current_animal.upper()}!",
            font=("Arial", 48, "bold"),
            fg="#00695c"
        )
    except Exception as e:
        print(f"Error showing animal: {e}")

def show_gif_with_audio(gif_name, audio_file=None, duration=2000, loop=False):
    """Show GIF and play audio simultaneously"""
    global gif_running, current_gif_frames
    
    clear_listening_screen()
    
    gif_running = False
    root.update()
    gif_running = True

    try:
        gif_path = os.path.join(GIF_PATH, gif_name)
        gif_image = Image.open(gif_path)
        current_gif_frames = [
            ImageTk.PhotoImage(frame.resize(
                (root.winfo_screenwidth(), root.winfo_screenheight())))
            for frame in ImageSequence.Iterator(gif_image)
        ]

        if audio_file:
            play_audio_non_blocking(audio_file)

        def animate(idx=0):
            if not gif_running:
                return
            
            if not loop and idx >= len(current_gif_frames):
                if current_gif_frames:
                    image_label.config(image=current_gif_frames[-1])
                return
                
            image_label.config(image=current_gif_frames[idx % len(current_gif_frames)])
            root.after(100, animate, idx + 1)

        animate()
        
        if not loop:
            root.after(duration, stop_gif)
    except Exception as e:
        print(f"Error showing GIF: {e}")

def stop_gif():
    global gif_running
    gif_running = False

# ---------- START SCREEN ----------

def show_start_screen():
    """Display welcome screen with GIF, name entry, and start button"""
    global child_name, accepting_input
    
    accepting_input = False
    
    for widget in main_frame.winfo_children():
        widget.pack_forget()
    
    start_container = tk.Frame(main_frame, bg="#e0f7fa")
    start_container.pack(expand=True)
    
    gif_label = tk.Label(start_container, bg="#e0f7fa")
    gif_label.pack(pady=20)
    
    try:
        gif_path = os.path.join(GIF_PATH, "default_level2.gif")
        gif_image = Image.open(gif_path)
        gif_frames = [
            ImageTk.PhotoImage(frame.resize((600, 400)))
            for frame in ImageSequence.Iterator(gif_image)
        ]
        
        frame_count = [0]
        
        def animate_start_gif():
            if frame_count[0] < len(gif_frames) and gif_label.winfo_exists():
                gif_label.config(image=gif_frames[frame_count[0]])
                gif_label.image = gif_frames[frame_count[0]]
                frame_count[0] += 1
                root.after(100, animate_start_gif)
            elif gif_label.winfo_exists():
                gif_label.config(image=gif_frames[-1])
                gif_label.image = gif_frames[-1]
        
        animate_start_gif()
    except Exception as e:
        print(f"Error loading start GIF: {e}")
    
    name_frame = tk.Frame(start_container, bg="#e0f7fa")
    name_frame.pack(pady=30)
    
    title_label = tk.Label(
        name_frame,
        text="🎵 LEVEL 3: Audio Matching 🎵",
        font=("Arial", 36, "bold"),
        bg="#e0f7fa",
        fg="#006064"
    )
    title_label.pack(pady=10)
    
    name_label = tk.Label(
        name_frame, 
        text="Enter Your Name:", 
        font=("Arial", 32, "bold"),
        bg="#e0f7fa",
        fg="#00838f"
    )
    name_label.pack(pady=10)
    
    name_entry = tk.Entry(
        name_frame,
        font=("Arial", 28),
        width=20,
        justify="center",
        bg="white",
        fg="#006064",
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
        print(f"Starting Level 3 for: {child_name}")
        start_container.destroy()
        start_game()
    
    name_entry.bind("<Return>", lambda e: start_game_clicked())
    
    start_btn = tk.Button(
        name_frame,
        text="START",
        font=("Arial", 32, "bold"),
        bg="#00acc1",
        fg="white",
        activebackground="#00838f",
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
    global accepting_input
    
    image_label.pack(expand=True)
    status_label.pack()
    
    accepting_input = False
    show_new_animal()

def show_new_animal():
    global current_animal, retry_count, question_count, accepting_input

    if question_count >= TOTAL_QUESTIONS:
        show_final_score()
        return

    stop_gif()
    clear_listening_screen()
    
    retry_count = 0
    current_animal = random.choice(animal_list)
    question_count += 1

    print(f"Question {question_count}: {current_animal}")

    try:
        # Show listening screen
        show_listening_screen()
        status_label.config(
            text=f"Question {question_count}/{TOTAL_QUESTIONS}",
            font=("Arial", 28),
            fg="#006064"
        )
        
        # Play animal sound
        root.after(500, play_animal_sound)
        
        # Enable input after sound plays
        root.after(2500, lambda: setattr(sys.modules[__name__], 'accepting_input', True))
        
    except Exception as e:
        print(f"Error in show_new_animal: {e}")

def check_rfid():
    global retry_count, score, accepting_input

    if ser.in_waiting:
        uid = ser.readline().decode(errors="ignore").strip().upper()
        
        if not uid or not accepting_input or current_animal is None:
            root.after(100, check_rfid)
            return
            
        print(f"RFID scanned: {uid}")
        
        accepting_input = False

        if uid == animal_to_uid[current_animal]:
            score += 1
            
            # Show animal image with name
            show_animal_with_name()
            root.after(2000, lambda: show_gif_with_audio(
                "goodJob.gif",
                os.path.join(SOUND_PATH, "correct_sound.mp3"),
                duration=2000
            ))
            root.after(4500, show_new_animal)

        else:
            retry_count += 1
            if retry_count < MAX_RETRIES:
                show_gif_with_audio(
                    "tryAgain.gif",
                    os.path.join(SOUND_PATH, "incorrect_sound.mp3"),
                    duration=1500
                )
                
                def retry_sound():
                    show_listening_screen()
                    root.after(500, play_animal_sound)
                    root.after(2500, lambda: setattr(sys.modules[__name__], 'accepting_input', True))
                
                root.after(1600, retry_sound)
            else:
                show_gif_with_audio(
                    "uhOh.gif",
                    os.path.join(SOUND_PATH, "oops_sound.mp3"),
                    duration=2000
                )
                root.after(2500, show_new_animal)
    
    root.after(100, check_rfid)

def show_final_score():
    """Display final score with completion message"""
    global gif_running, current_gif_frames, accepting_input
    
    accepting_input = False
    stop_gif()
    clear_listening_screen()
    
    save_results_to_excel()
    
    percentage = (score / TOTAL_QUESTIONS) * 100
    
    status_label.pack_forget()
    image_label.pack_forget()
    
    final_container = tk.Frame(main_frame, bg="#e0f7fa")
    final_container.pack(expand=True)
    
    final_gif_label = tk.Label(final_container, bg="#e0f7fa")
    final_gif_label.pack(pady=20)
    
    # Different message if launched from launcher vs standalone
    if child_name and len(sys.argv) > 1:
        score_text = f"🎉 Congratulations, {child_name}! 🎉\n\nYou completed all 3 levels!\n\nLevel 3 Score: {score}/{TOTAL_QUESTIONS} ({percentage:.1f}%)"
    else:
        score_text = f"Awesome, {child_name}!\n\nYou matched {score} out of {TOTAL_QUESTIONS} sounds correctly!\n\nScore: {percentage:.1f}%"
    
    score_label = tk.Label(
        final_container,
        text=score_text,
        font=("Arial", 32, "bold"),
        bg="#e0f7fa",
        fg="#006064",
        justify="center"
    )
    score_label.pack(pady=30)
    
    try:
        gif_path = os.path.join(GIF_PATH, "finalScore.gif")
        gif_image = Image.open(gif_path)
        final_frames = [
            ImageTk.PhotoImage(frame.resize((600, 400)))
            for frame in ImageSequence.Iterator(gif_image)
        ]
        
        frame_count = [0]
        
        def animate_final_gif():
            if frame_count[0] < len(final_frames) and final_gif_label.winfo_exists():
                final_gif_label.config(image=final_frames[frame_count[0]])
                final_gif_label.image = final_frames[frame_count[0]]
                frame_count[0] += 1
                root.after(100, animate_final_gif)
            elif final_gif_label.winfo_exists():
                final_gif_label.config(image=final_frames[-1])
                final_gif_label.image = final_frames[-1]
        
        animate_final_gif()
    except Exception as e:
        print(f"Error loading final GIF: {e}")
    
    buttons_frame = tk.Frame(final_container, bg="#e0f7fa")
    buttons_frame.pack(pady=20)
    
    # Show Home button only if launched from launcher
    if len(sys.argv) > 1:
        home_btn = tk.Button(
            buttons_frame,
            text="🏠 Back to Home",
            font=("Arial", 28, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            relief="raised",
            bd=5,
            padx=40,
            pady=15,
            command=go_home,
            cursor="hand2"
        )
        home_btn.pack(side="left", padx=10)
    
    exit_btn = tk.Button(
        buttons_frame,
        text="EXIT",
        font=("Arial", 28, "bold"),
        bg="#e63946",
        fg="white",
        activebackground="#d62828",
        activeforeground="white",
        relief="raised",
        bd=5,
        padx=40,
        pady=15,
        command=exit_app,
        cursor="hand2"
    )
    exit_btn.pack(side="left", padx=10)

# ---------- START ----------
if child_name:
    # Name provided from launcher - skip name entry
    print(f"Level 3 started for: {child_name}")
    start_game()
else:
    # No name provided - show name entry
    show_start_screen()
    
check_rfid()
root.mainloop()