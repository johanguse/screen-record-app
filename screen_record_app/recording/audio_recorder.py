from PyQt6.QtCore import QThread
import pyaudio

class AudioRecorder(QThread):
    def __init__(self):
        super().__init__()
        self.audio_data = []
        self.is_recording = False

    def run(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        self.is_recording = True

        while self.is_recording:
            data = stream.read(CHUNK)
            self.audio_data.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self.is_recording = False

    def get_audio_data(self):
        """Joins all collected audio byte chunks, clears the list, and returns the joined data."""
        joined_data = b''.join(self.audio_data)
        self.clear_audio_data()
        return joined_data

    def clear_audio_data(self):
        """Resets the audio_data list to empty."""
        self.audio_data = []