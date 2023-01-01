# Import statements
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech.audio import AudioOutputConfig
import subprocess
import tkinter as tk

# Function to configure the speech synthesizer
def configure_speech_synthesizer(speech_key, service_region, voice_name="en-US-JessaNeural"):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = voice_name
    return speech_config

def synthesize_and_play(speech_config, text_box):
    # Create an audio configuration that will write the synthesized audio to a file
    audio_config = speechsdk.audio.AudioOutputConfig(filename="output.wav")
    # Create a synthesizer with the given settings
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    # Get the text from the text box
    text = text_box.get("1.0", "end-1c")
    # Synthesize the text
    result = synthesizer.speak_text_async(text).get()
    # Check the result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized to speaker for text [{}]".format(text))
        # Play the audio, do not open a prompt, use subprocess instead of os.system to avoid blocking the GUI
        # os.system("audiology.exe output.wav") 
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen(["audiology.exe", "output.wav"], startupinfo=si)
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
        print("Did you update the subscription info?")

    # Clear the text box and any text that was in it
    text_box.delete("1.0", "end")

def main(speech_config):    
    # Create a simple GUI using tkinter
    root = tk.Tk()
    root.title("Text to Speech - Neural Synthesis")
    root.geometry("800x148")
    # Disable resizing the GUI
    root.resizable(False, False)

    # Add a drop-down menu to select the voices from voice_options.txt
    voice_options = []
    with open("voice_options.txt", "r") as f:
        for line in f:
            voice_options.append(line.strip())
    voice_var = tk.StringVar(root)

    # Set the default voice to the first one in the list
    voice_var.set(voice_options[0])

    # Create a label for the text to be synthesized, should be on left above the text box
    label = tk.Label(root, text="Enter the text to be synthesized: ")
    label.pack()

    # Create a text box for the user to enter the text to be synthesized
    text_box = tk.Text(root, height=5, width=100)
    text_box.pack()

    # Put a horizontal line between the text box and the button
    separator = tk.Frame(height=2, bd=1, relief=tk.SUNKEN)
    separator.pack(fill=tk.X, padx=5, pady=5)

    # Create a button to synthesize the text and then play the audio.
    button = tk.Button(root, text="Synthesize and Play", command=lambda: synthesize_and_play(speech_config, text_box))
    button.pack()

    # Configure the button to be pressed if I hit Ctrl+Enter
    root.bind("<Return>", lambda event: synthesize_and_play(speech_config, text_box))
    
    # Start the GUI
    root.mainloop()

# Call the main function
if __name__ == "__main__":
    # Read the voice from a config file called voice.txt, remove any newlines
    with open("voice.txt", "r") as f:
        voice = f.read().replace("\n", "")
    # Configure the speech synthesizer
    speech_config = configure_speech_synthesizer("<INSERT KEY HERE>", "eastus", voice)
    main(speech_config)
