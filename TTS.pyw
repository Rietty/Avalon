# Import statements
import os
import tkinter as tk

import sounddevice as sd
from dotenv import load_dotenv
from elevenlabs import play
from elevenlabs.client import ElevenLabs


def synthesize_and_play(client: ElevenLabs, text_box: tk.Text):
    audio = client.text_to_speech.convert(
        text=text_box.get("1.0", "end-1c"),
        voice_id="aEO01A4wXwd1O8GPgGlF",
        model_id="eleven_flash_v2_5",
        output_format="mp3_44100_128",
        optimize_streaming_latency=1,
    )

    play(audio, use_ffmpeg=False)

    text_box.delete("1.0", "end")

def main(client: ElevenLabs):
    # Create a simple GUI using tkinter
    root = tk.Tk()
    root.title("Text to Speech - Neural Synthesis")
    root.geometry("800x150")
    # Disable resizing the GUI
    root.resizable(False, False)

    # Create a label for the text to be synthesized, should be on left above the text box
    label = tk.Label(root, text="Enter the text to be synthesized: ")
    label.pack()

    # Create a text box for the user to enter the text to be synthesized
    text_box = tk.Text(root, height=5, width=100)
    text_box.pack()

    # Put a horizontal line between the text box and the button
    separator = tk.Frame(height=2, bd=1, relief=tk.SUNKEN)
    separator.pack(fill=tk.X, padx=5, pady=5)

    # Create a button to synthesize the text and then play the audio. Visually hide the button
    button = tk.Button(
        root,
        text="Synthesize and Play",
        command=lambda: synthesize_and_play(client, text_box),
    )
    button.pack()

    # Configure the button to be pressed if I hit Ctrl+Enter
    root.bind("<Return>", lambda event: synthesize_and_play(client, text_box))

    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    load_dotenv()
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    sd.default.device = 5
    main(client)