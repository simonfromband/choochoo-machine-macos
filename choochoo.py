#TO THOSE WHO IT MAY CONCERN: don't python on or for a mac
import mido
import pygame
import tkinter as tk
import os
import customtkinter as ctk
import sys
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import time

# Where files??
def get_resources_path():
    if getattr(sys, 'frozen', False):  # If running from a bundled app
        return os.path.join(os.path.dirname(sys.executable), 'Resources')
    else:
        return os.path.join(os.path.dirname(__file__), 'Resources')

# START YOUR pygames ...with pre_init so the thing workss
try:
    pygame.mixer.pre_init(44100, -16, 2, 2048)  # THE THING THAT MAKES MACOS WORK
    pygame.mixer.init()
except pygame.error as e:
    print(f"Error initializing pygame mixer: {e}", file=sys.stderr)
    sys.exit(1)

class MidiPlayerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Shawnee Heights Choo Choo Machine 9000")

        self.master.resizable(False, False)

        # resource path
        self.resources_path = get_resources_path()

        # Load audio files
        self.audio_files = self.load_audio_files()

        self.buttons = {}
        self.error_buttons = set()
        self.currently_playing = None
        self.midi_device_connected = False
        self.midi_listener_active = False  # Tracks if MIDI listener is active

        # computer keyboard bindings
        self.key_to_sample = {
            '1': 95,
            '2': 96,
            '3': 98,
            '4': 100,
            '5': 101,
            '6': 103,
            '7': 105,
            '8': 107,
            '9': 108
        }
#OH BROTHER
        # get screen and window siz
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        window_width = 840
        window_height = 600

        # open to the middle of the screen?? brother this aint workin
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2 - 100

        self.master.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Button grid
        self.frame = tk.Frame(master)
        self.frame.pack(side=tk.LEFT, padx=10, pady=10)

        # frame for connection status and goofy ahhh pic
        self.top_frame = tk.Frame(master)
        self.top_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # MIDI connection status
        self.midi_status_label = ctk.CTkLabel(
            self.top_frame,
            text="Ayyo, I'm not connected to the Synth. Plug me in, coach!",
            text_color="red",
            font=("Arial", 12)
        )
        self.midi_status_label.pack(pady=(10, 5))
        self.image_path = os.path.join(self.resources_path, "pic.png")
        self.load_and_display_image()


#THIS GUY STINKSSS!!!

        
        # Clickable playback buttons
        for audio_file, midi_note, display_name in self.audio_files:
            button_frame = tk.Frame(self.frame)
            button_frame.pack(pady=10)
            if os.path.isfile(audio_file):
                button_text = f"Play {display_name}"
                fg_color = "grey"
                hover_color = "#404040"  # Darker grey for hover
                text_color = "white"
            else:
                button_text = f"Where's {display_name}??🤨🤨"
                fg_color = "red"
                hover_color = "#a00a00"  # Darker red for hover
                text_color = "white"
                self.error_buttons.add(midi_note)
            play_button = ctk.CTkButton(
                button_frame,
                text=button_text,
                command=lambda af=audio_file, mn=midi_note, dn=display_name: self.play_audio_file(af, mn, dn),
                fg_color=fg_color,
                hover_color=hover_color,  # Set hover color
                text_color=text_color,
                width=200
            )
            play_button.pack(side=tk.LEFT, padx=5)
            self.buttons[midi_note] = play_button




        
        # Reset button
        self.reset_button = ctk.CTkButton(
            self.frame,
            text="Reset Button Colors [DELETE]",
            command=self.reset_button_colors,
        )
        self.reset_button.pack(pady=10)

        
        # Stop playback button
        self.stop_button = ctk.CTkButton(
            self.frame, 
            text="Stop Playback [SPACEBAR]", 
            command=self.stop_playback,
            fg_color="red", 
            text_color="white",
            hover_color="#c00"  # Darker red for hover
        )
        self.stop_button.pack(pady=10)



        
# Actually do stuff with the computer keyboard. useless unless parker borks the synth or something
        self.master.bind("<space>", self.trigger_stop_playback)
        self.master.bind("<BackSpace>", self.trigger_reset_button)
        for key, midi_note in self.key_to_sample.items():
            self.master.bind(f"<KeyPress-{key}>", lambda event, note=midi_note: self.trigger_sample(note))
# Start MIDI listener thread!!!!!!!!
        threading.Thread(target=self.check_midi_device_status, daemon=True).start()
    def load_audio_files(self):
        """Helper to load audio file paths and ensure they exist."""
        files = [
            ("sample 1.mp3", 95, "Sample 1"),
            ("sample 2.mp3", 96, "Sample 2"),
            ("sample 3.mp3", 98, "Sample 3"),
            ("sample 4.mp3", 100, "Sample 4"),
            ("sample 5.mp3", 101, "Sample 5"),
            ("sample 6.mp3", 103, "Sample 6"),
            ("sample 7.mp3", 105, "Sample 7"),
            ("sample 8.mp3", 107, "Sample 8"),
            ("sample 9.mp3", 108, "Sample 9")
        ]
        return [(os.path.join(self.resources_path, f), midi_note, name) for f, midi_note, name in files]

    
#skull emoji

    
    def stop_playback(self):
        pygame.mixer.music.stop()
        if self.currently_playing:
            self.update_button_label(self.currently_playing, f"Already Played {self.get_display_name(self.currently_playing)}")
            self.update_button_color(self.currently_playing, "orange", "#cc8400", "black")  # Darker orange for hover and black text
        self.currently_playing = None

    def load_and_display_image(self):
        """Load and display the image."""
        try:
            image = Image.open(self.image_path)
            photo = ImageTk.PhotoImage(image)
            image_label = tk.Label(self.top_frame, image=photo)
            image_label.image = photo
            image_label.pack(pady=10)
        except Exception as e:
            print(f"Error loading image: {e}", file=sys.stderr)



    
    def play_audio_file(self, audio_file, midi_note, display_name):
        """Play the selected audio file and update button color."""
        try:
            if self.currently_playing:
                self.update_button_label(self.currently_playing, f"Already Played {self.get_display_name(self.currently_playing)}")
                self.update_button_color(self.currently_playing, "orange", "#cc8400", "black")

            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            self.update_button_label(midi_note, f"Now Playing {display_name}...")
            self.update_button_color(midi_note, "#009900", "green", "white")
            self.currently_playing = midi_note
            self.master.after(100, self.check_music_playback)
        except pygame.error as e:
            print(f"Error playing {audio_file}: {e}", file=sys.stderr)


    
    def check_music_playback(self):
        """Check if the music is still playing, and update button color."""
        if not pygame.mixer.music.get_busy():
            if self.currently_playing:
                self.update_button_label(self.currently_playing, f"Already Played {self.get_display_name(self.currently_playing)}")
                self.update_button_color(self.currently_playing, "orange", "#cc8400", "black")  # Darker orange for hover and black text
            self.currently_playing = None
        else:
            self.master.after(100, self.check_music_playback)

    def update_button_color(self, midi_note, color, hover_color, text_color):
        """Update the button color based on the MIDI note."""
        if midi_note in self.buttons:
            button = self.buttons[midi_note]
            button.configure(fg_color=color, hover_color=hover_color, text_color=text_color)
    def update_button_label(self, midi_note, text):
        """Update the button label text based on the MIDI note."""
        if midi_note in self.buttons:
            button = self.buttons[midi_note]
            button.configure(text=text)
    def get_display_name(self, midi_note):
        """Get the display name for the given MIDI note."""
        for _, note, name in self.audio_files:
            if note == midi_note:
                return name
        return "Unknown"





    
    def reset_button_colors(self):
        """Stop playback and reset button colors to grey, except for missing samples."""
        self.stop_playback()
        for midi_note in self.buttons:
            if midi_note in self.error_buttons:
                self.update_button_color(midi_note, "red", "#a00a00", "white")  # Darker red for hover and white text
                self.update_button_label(midi_note, f"Where's {self.get_display_name(midi_note)}??🤨🤨")
            else:
                self.update_button_color(midi_note, "grey", "#404040", "white")  # Darker grey for hover and white text
                self.update_button_label(midi_note, f"Play {self.get_display_name(midi_note)}")



    
    def check_midi_device_status(self):
        """Continuously check the MIDI device status and update the label."""
        while True:
            input_names = mido.get_input_names()
            if input_names and not self.midi_device_connected:
                self.midi_status_label.configure(text="Synth and Laptop are connected. Nice work!", text_color="green")
                threading.Thread(target=self.start_midi_listener, daemon=True).start()  # Start MIDI listener
                self.midi_device_connected = True
            elif not input_names and self.midi_device_connected:
                self.midi_status_label.configure(text="No MIDI device connected", text_color="red")
                self.midi_device_connected = False
            time.sleep(1)


    
    def start_midi_listener(self):
        """Start listening for MIDI input and process MIDI events."""
        try:
            input_names = mido.get_input_names()
            if input_names:
                with mido.open_input(input_names[0]) as midi_input:
                    for msg in midi_input:
                        if msg.type == 'note_on' and msg.velocity > 0:
                            midi_note = msg.note
                            for audio_file, note, _ in self.audio_files:
                                if note == midi_note:
                                    self.play_audio_file(audio_file, note, self.get_display_name(note))
                                    break
        except Exception as e:
            print(f"MIDI Error: {e}", file=sys.stderr)
            self.midi_status_label.configure(text="MIDI error detected", text_color="red")
    def trigger_stop_playback(self, event):
        """Trigger the stop playback button."""
        self.stop_playback()
    def trigger_reset_button(self, event):
        """Trigger the reset button."""
        self.reset_button_colors()
    def trigger_sample(self, midi_note):
        """Trigger a sample based on the number key pressed."""
        for audio_file, note, display_name in self.audio_files:
            if note == midi_note:
                self.play_audio_file(audio_file, note, display_name)
                break
if __name__ == "__main__":
    root = ctk.CTk()
    app = MidiPlayerApp(root)
    root.mainloop()
