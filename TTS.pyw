# Import statements
import logging
import os
import sys


def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


import sounddevice as sd
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
from PyQt6 import QtCore, QtGui, QtWidgets

# All voices
voices = {
    "Blondie": "exsUS4vynmxd379XN4yO",
}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


def synthesize_and_play(client: ElevenLabs, text: str, voice_id: str):
    logging.info(f"Synthesizing text: {text!r}")

    try:
        audio = client.text_to_speech.stream(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            optimize_streaming_latency=1,
        )
        logging.info("Audio synthesis successful, playing audio.")
        play(audio, use_ffmpeg=False)
        logging.info("Audio playback finished.")
    except Exception as e:
        logging.error(f"Error during synthesis or playback: {e}")


class EnterToSpeakEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, on_enter):
        super().__init__()
        self.on_enter = on_enter

    def keyPressEvent(self, event):  # ty:ignore[invalid-method-override]
        if event.key() in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
            if event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier:
                return super().keyPressEvent(event)
            self.on_enter()
            return
        return super().keyPressEvent(event)


class TitleBar(QtWidgets.QWidget):
    """Custom draggable title bar so the window chrome matches the theme."""

    def __init__(self, window: QtWidgets.QWidget, title: str):
        super().__init__()
        self._window = window
        self._drag_pos = None
        self.setObjectName("TitleBar")
        self.setFixedHeight(36)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 6, 0)
        layout.setSpacing(8)

        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("TitleBarLabel")
        title_label.setFont(QtGui.QFont("JetBrains Mono", 9, QtGui.QFont.Weight.Medium))
        layout.addWidget(title_label)
        layout.addStretch(1)

        minimize_btn = QtWidgets.QPushButton("–")  # en dash
        minimize_btn.setObjectName("TitleBarButton")
        minimize_btn.setFixedSize(28, 24)
        minimize_btn.clicked.connect(self._window.showMinimized)
        layout.addWidget(minimize_btn)

        close_btn = QtWidgets.QPushButton("✕")  # multiplication x
        close_btn.setObjectName("CloseButton")
        close_btn.setFixedSize(28, 24)
        close_btn.clicked.connect(self._window.close)
        layout.addWidget(close_btn)

    def mousePressEvent(self, event):  # ty:ignore[invalid-method-override]
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self._window.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):  # ty:ignore[invalid-method-override]
        if (
            self._drag_pos is not None
            and event.buttons() == QtCore.Qt.MouseButton.LeftButton
        ):
            self._window.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):  # ty:ignore[invalid-method-override]
        self._drag_pos = None


class FramelessWindow(QtWidgets.QWidget):
    """Borderless window; dragging is handled by the custom TitleBar."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)


def main(client: ElevenLabs):
    app = QtWidgets.QApplication([])

    with open(resource_path("style.qss")) as f:
        app.setStyleSheet(f.read())

    app.setWindowIcon(QtGui.QIcon(resource_path("icon.ico")))

    window = FramelessWindow()
    window.setWindowTitle("Text to Speech - Neural Synthesis")
    window.resize(800, 256)
    window.setMinimumSize(520, 220)

    # Outer layout: custom title bar on top, content container below.
    outer = QtWidgets.QVBoxLayout(window)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)

    title_bar = TitleBar(window, "Text to Speech - Neural Synthesis")
    outer.addWidget(title_bar)

    container = QtWidgets.QWidget()
    container.setObjectName("Container")
    outer.addWidget(container)

    layout = QtWidgets.QVBoxLayout(container)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(10)

    title = QtWidgets.QLabel("Enter the text to be synthesized:")
    title.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Weight.Medium))
    layout.addWidget(title)

    voice_row = QtWidgets.QHBoxLayout()
    voice_label = QtWidgets.QLabel("Voice:")
    voice_label.setFont(QtGui.QFont("Segoe UI", 9))
    voice_combo = QtWidgets.QComboBox()
    voice_combo.setFont(QtGui.QFont("Segoe UI", 9))
    for name in voices.keys():
        voice_combo.addItem(name)
    voice_row.addWidget(voice_label)
    voice_row.addWidget(voice_combo)
    voice_row.addStretch(1)
    layout.addLayout(voice_row)

    text_box = EnterToSpeakEdit(lambda: None)
    text_box.setPlaceholderText(
        "Type here and press Enter to speak. Shift+Enter inserts a new line."
    )
    text_box.setFont(QtGui.QFont("Segoe UI", 10))
    text_box.setTabChangesFocus(True)
    layout.addWidget(text_box)

    separator = QtWidgets.QFrame()
    separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
    separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
    layout.addWidget(separator)

    hint = QtWidgets.QLabel("Press Enter to speak. Shift+Enter for a new line.")
    hint.setFont(QtGui.QFont("Segoe UI", 8))
    hint.setStyleSheet("color: #5a5a5a;")
    layout.addWidget(hint)

    def on_enter():
        text = text_box.toPlainText().strip()
        if not text:
            return
        voice_name = voice_combo.currentText()
        voice_id = voices.get(voice_name, voices["Blondie"])
        synthesize_and_play(client, text, voice_id)
        text_box.clear()

    text_box.on_enter = on_enter
    text_box.setFocus()

    window.show()
    app.exec()


if __name__ == "__main__":
    load_dotenv()
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    sd.default.device = 5
    main(client)
