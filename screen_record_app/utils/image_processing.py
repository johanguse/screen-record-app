import cv2
from PyQt6.QtGui import QImage
import numpy as np

def overlay_webcam(screenshot, webcam_frame, position):
    webcam_height, webcam_width = webcam_frame.shape[:2]
    screen_height, screen_width = screenshot.shape[:2]
    
    # Calculate webcam frame size (20% of screen width)
    new_webcam_width = int(screen_width * 0.2)
    new_webcam_height = int(webcam_height * new_webcam_width / webcam_width)
    
    webcam_frame = cv2.resize(webcam_frame, (new_webcam_width, new_webcam_height))
    
    # Determine position
    if position == 'top-left':
        x, y = 0, 0
    elif position == 'top-right':
        x, y = screen_width - new_webcam_width, 0
    elif position == 'bottom-left':
        x, y = 0, screen_height - new_webcam_height
    else:  # bottom right
        x, y = screen_width - new_webcam_width, screen_height - new_webcam_height
    
    # Create a mask for the webcam frame
    mask = np.zeros(screenshot.shape[:2], dtype=np.uint8)
    mask[y:y+new_webcam_height, x:x+new_webcam_width] = 255

    # Blend the webcam frame with the screenshot
    screenshot_bg = cv2.bitwise_and(screenshot, screenshot, mask=cv2.bitwise_not(mask))
    webcam_fg = cv2.bitwise_and(webcam_frame, webcam_frame, mask=mask[y:y+new_webcam_height, x:x+new_webcam_width])
    
    screenshot[y:y+new_webcam_height, x:x+new_webcam_width] = webcam_fg

    return screenshot

def create_qimage(frame):
    if len(frame.shape) != 3 or frame.shape[2] != 3:
        print(f"Unexpected frame shape: {frame.shape}")
        return None
    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    height, width, channel = frame.shape
    bytes_per_line = 3 * width
    try:
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        return q_image
    except Exception as e:
        print(f"Error creating QImage: {str(e)}")
        return None