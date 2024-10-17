import os
import tkinter as tk
import sounddevice as sd
import numpy as np
import wave
import datetime
from common import *

# Ensure class directories exist
for cls in CLASSES:
    class_dir = os.path.join(DATA_DIR, cls)
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)

class AudioRecorder:
    def __init__(self, master):
        self.master = master
        self.master.title("Audio Recorder")
        self.current_class_index = 0

        # Display current class
        self.class_var = tk.StringVar()
        self.class_var.set(f"Current Class: {CLASSES[self.current_class_index]}")
        self.label = tk.Label(master, textvariable=self.class_var, font=('Arial', 24))
        self.label.pack(pady=20)

        # Instructions
        self.instructions = tk.Label(master, text="Use Left/Right Arrow keys to change class.\nPress Spacebar to record.", font=('Arial', 14))
        self.instructions.pack(pady=10)

        # Status message
        self.status_var = tk.StringVar()
        self.status_var.set("")
        self.status_label = tk.Label(master, textvariable=self.status_var, font=('Arial', 14))
        self.status_label.pack(pady=10)

        # Bind keys
        master.bind('<Left>', self.prev_class)
        master.bind('<Right>', self.next_class)
        master.bind('<space>', self.record_audio)

        # Focus on the window to capture key events
        master.focus_set()

    def prev_class(self, event):
        self.current_class_index = (self.current_class_index - 1) % len(CLASSES)
        self.class_var.set(f"Current Class: {CLASSES[self.current_class_index]}")

    def next_class(self, event):
        self.current_class_index = (self.current_class_index + 1) % len(CLASSES)
        self.class_var.set(f"Current Class: {CLASSES[self.current_class_index]}")

    def record_audio(self, event):
        self.status_var.set("Recording...")
        self.master.update_idletasks()
        print("Recording started...")
        audio_data = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()
        print("Recording finished.")
        self.status_var.set("Recording finished.")
        self.save_audio(audio_data)

    def save_audio(self, audio_data):
        # Convert float32 data to int16
        audio_int16 = np.int16(audio_data * 32767)

        # Save to the appropriate class directory
        class_name = CLASSES[self.current_class_index]
        class_dir = os.path.join(DATA_DIR, class_name)

        # Ensure the class directory exists
        os.makedirs(class_dir, exist_ok=True)

        # List existing files in the directory
        files = os.listdir(class_dir)

        # Extract numbers from filenames
        numbers = []
        for f in files:
            if f.endswith('.wav'):
                name_part = f[:-4]  # Remove '.wav'
                try:
                    number = int(name_part)
                    numbers.append(number)
                except ValueError:
                    pass  # Skip files that don't have numeric names

        # Determine the next highest number
        if numbers:
            next_number = max(numbers) + 1
        else:
            next_number = 1  # Start from 1 if no files are present

        # Create the filename using the next highest number
        filename = f"{next_number}.wav"
        file_path = os.path.join(class_dir, filename)

        # Write WAV file
        with wave.open(file_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes for int16
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())

        self.status_var.set(f"Saved: {file_path}")
        print(f"Saved audio to {file_path}")
        
if __name__ == "__main__":
    select_audio_input_device()

    root = tk.Tk()
    app = AudioRecorder(root)
    root.mainloop()
