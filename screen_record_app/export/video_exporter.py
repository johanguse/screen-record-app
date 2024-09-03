from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QThread, QObject, pyqtSignal, QSettings
import os
import tempfile
from datetime import datetime
import cv2
import subprocess
import shutil
import wave
import time
import struct
from .video_enhancer import VideoEnhancerThread
from screen_record_app.utils.retry_operation import retry_operation

from PyQt6.QtCore import QThread, pyqtSignal

class ExportThread(QThread):
    progress = pyqtSignal(int)
    completed = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, video_exporter, frames, audio_data, output_path, output_format, enhance, add_watermark, watermark_path):
        super().__init__()
        self.video_exporter = video_exporter
        self.frames = frames
        self.audio_data = audio_data
        self.output_path = output_path
        self.output_format = output_format
        self.enhance = enhance
        self.add_watermark = add_watermark
        self.watermark_path = watermark_path

    def run(self):
        try:
            self.video_exporter.export_video(
                self.frames, self.audio_data, self.output_path, self.output_format, 
                self.enhance, self.add_watermark, self.watermark_path
            )
            self.completed.emit()
        except Exception as e:
            self.error.emit(str(e))

class VideoExporter(QObject):
    export_progress = pyqtSignal(int)
    export_completed = pyqtSignal()
    export_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.app_name = "screen_record_app"  # Get this from pyproject.toml
        self.settings = QSettings("YourCompany", "CaptureCanvasPro")
        self.last_save_directory = self.settings.value("last_save_directory", os.path.expanduser("~"))

    def check_ffmpeg(self):
        """Check if FFmpeg is available in the system PATH."""
        return shutil.which('ffmpeg') is not None
    
    def start_export(self, frames, audio_data, output_format, enhance, add_watermark=False, watermark_path=None):
        if not self.check_ffmpeg():
            self.export_error.emit("FFmpeg not found on the system.")
            return

        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{self.app_name}_{current_datetime}.{output_format.lower()}"

        output_path, _ = QFileDialog.getSaveFileName(
            None,
            "Save Video",
            os.path.join(self.last_save_directory, default_filename),
            f"{output_format.upper()} Files (*.{output_format.lower()})"
        )

        if not output_path:
            return

        # Save the directory for next time
        self.last_save_directory = os.path.dirname(output_path)
        self.settings.setValue("last_save_directory", self.last_save_directory)

        # Start the export in a new thread
        self.export_thread = ExportThread(self, frames, audio_data, output_path, output_format, enhance, add_watermark, watermark_path)
        self.export_thread.progress.connect(self.export_progress.emit)
        self.export_thread.completed.connect(self.export_completed.emit)
        self.export_thread.error.connect(self.export_error.emit)
        self.export_thread.start()

    def export_video(self, frames, audio_data, output_path, output_format, enhance, add_watermark=False, watermark_path=None):
        try:
            temp_video_path = tempfile.mktemp(suffix='.mp4')
            temp_audio_path = tempfile.mktemp(suffix='.wav')

            # Save frames to video
            self.save_frames_to_video(frames, temp_video_path, enhance)
            self.export_progress.emit(25)  # 25% progress after saving frames

            # Save audio to file
            self.save_audio_to_file(audio_data, temp_audio_path)
            self.export_progress.emit(50)  # 50% progress after saving audio

            # Combine audio and video
            self.combine_audio_video(temp_video_path, temp_audio_path, output_path, add_watermark, watermark_path)

            # Cleanup temporary files
            os.remove(temp_video_path)
            os.remove(temp_audio_path)

            self.export_completed.emit()
        except Exception as e:
            self.export_error.emit(str(e))

    def save_frames_to_video(self, frames, output_path, enhance):
        if not frames:
            raise ValueError("No frames to export")

        height, width, _ = frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))

        for frame in frames:
            if enhance:
                frame = self.enhance_frame(frame)
            out.write(frame)

        out.release()

    def save_audio_to_file(self, audio_data, output_path):
        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            
            # Convert the list of audio samples to a byte string
            audio_bytes = struct.pack(f"{len(audio_data)}h", *audio_data)
            wf.writeframes(audio_bytes)

    def combine_audio_video(self, video_path, audio_path, output_path, add_watermark=False, watermark_path=None):
        try:
            command = ['ffmpeg', '-i', video_path, '-i', audio_path]
            
            if add_watermark and watermark_path:
                command.extend([
                    '-i', watermark_path,
                    '-filter_complex', '[0:v][2:v]overlay=main_w-overlay_w-10:main_h-overlay_h-10'
                ])
            
            command.extend(['-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental', output_path])
            
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            for line in process.stderr:
                if 'time=' in line:
                    try:
                        time_info = line.split('time=')[1].split()[0]
                        hours, minutes, seconds = map(float, time_info.split(':'))
                        total_seconds = hours * 3600 + minutes * 60 + seconds
                        total_duration = self.get_video_duration(video_path)
                        progress_value = int((total_seconds / total_duration) * 50) + 50
                        self.export_progress.emit(progress_value)
                    except ValueError:
                        continue

            process.wait()

            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command)

        except subprocess.CalledProcessError as e:
            raise Exception(f'FFmpeg error: {e}')

    def get_video_duration(self, video_path):
        command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return float(result.stdout)

    def enhance_frame(self, frame):
        # Apply basic image enhancement
        enhanced = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
        return enhanced

    def cleanup_temp_files(self, *file_paths):
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    for _ in range(5):  # Try up to 5 times
                        try:
                            os.remove(file_path)
                            break
                        except PermissionError:
                            time.sleep(1)  # Wait a second before retrying
                    else:
                        print(f"Failed to remove {file_path} after multiple attempts")
            except Exception as e:
                print(f"Error cleaning up temporary file {file_path}: {str(e)}")