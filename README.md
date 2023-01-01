# Avalon
This project is simply used to use Azure Speech Services to convert text to speech and play it back over a Virtual Audio Cable. Used mainly for Discord and other voice chat applications.

To use, build the Rust project and get the executable. Make sure the audio cable is set-up/marked correctly. `voice.txt` controls the voice currently active, the `voice_options.txt` is just available options, more can be found on Azure docs. Python script can be double-clicked to run the simple GUI program. The program basically uses Python to convert text to speech and save to a file, then uses Rust to play the file back over the Virtual Audio Cable.

![image](https://user-images.githubusercontent.com/35241556/210158189-fe253cfe-4a0f-475d-9df9-b022ee51db3b.png)
