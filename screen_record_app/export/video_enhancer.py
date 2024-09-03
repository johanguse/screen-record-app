from PyQt6.QtCore import QThread, pyqtSignal
import cv2

class VideoEnhancerThread(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, frames, output_path, output_format, enhance):
        super().__init__()
        self.frames = frames
        self.output_path = output_path
        self.output_format = output_format
        self.enhance = enhance

    def run(self):
        try:
            height, width = self.frames[0].shape[:2]
            if self.output_format == 'mp4':
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            elif self.output_format == 'avi':
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
            else:  # default to mp4
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            
            out = cv2.VideoWriter(f"{self.output_path}.{self.output_format}", fourcc, 30, (width, height))

            if self.enhance:
                try:
                    sr = cv2.dnn_superres.DnnSuperResImpl_create()
                    sr.readModel("ESPCN_x2.pb")  # You need to download this model file
                    sr.setModel("espcn", 2)
                except AttributeError:
                    self.error_occurred.emit("AI enhancement not available. Exporting without enhancement.")
                    self.enhance = False

            for i, frame in enumerate(self.frames):
                if self.enhance:
                    frame = sr.upsample(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                else:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                out.write(frame)
                self.progress_updated.emit(int((i + 1) / len(self.frames) * 100))

            out.release()
            self.finished.emit()
        except Exception as e:
            self.error_occurred.emit(f"An error occurred during video export: {str(e)}")