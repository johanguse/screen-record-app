import unittest
import numpy as np
from screen_record_app.utils.image_processing import overlay_webcam

class TestImageProcessing(unittest.TestCase):
    def setUp(self):
        """Set up for test methods."""
        self.main_frame_height = 480
        self.main_frame_width = 640
        self.webcam_frame_height = 120
        self.webcam_frame_width = 160
        
        self.main_frame = np.zeros((self.main_frame_height, self.main_frame_width, 3), dtype=np.uint8)
        self.webcam_frame = np.full((self.webcam_frame_height, self.webcam_frame_width, 3), 255, dtype=np.uint8) # White webcam frame

    def test_overlay_webcam_positions(self):
        """Test that overlay_webcam correctly places the webcam frame at different positions."""
        positions = {
            'top-left': (0, 0),
            'top-right': (0, self.main_frame_width - self.webcam_frame_width),
            'bottom-left': (self.main_frame_height - self.webcam_frame_height, 0),
            'bottom-right': (self.main_frame_height - self.webcam_frame_height, 
                             self.main_frame_width - self.webcam_frame_width)
        }

        for position_name, (start_y, start_x) in positions.items():
            with self.subTest(position=position_name):
                current_main_frame = self.main_frame.copy()
                result_frame = overlay_webcam(current_main_frame, self.webcam_frame, position_name)

                self.assertIsNotNone(result_frame, f"Result frame is None for position {position_name}")
                self.assertEqual(result_frame.shape, self.main_frame.shape, f"Result frame shape mismatch for {position_name}")

                # Define the slice for the webcam overlay area
                end_y = start_y + self.webcam_frame_height
                end_x = start_x + self.webcam_frame_width
                
                # Check a corner pixel of the overlaid area
                self.assertTrue(np.array_equal(result_frame[start_y, start_x], [255, 255, 255]), 
                                f"Top-left pixel of webcam overlay incorrect for {position_name}")
                
                # Check a central pixel of the overlaid area
                center_overlay_y = start_y + self.webcam_frame_height // 2
                center_overlay_x = start_x + self.webcam_frame_width // 2
                self.assertTrue(np.array_equal(result_frame[center_overlay_y, center_overlay_x], [255, 255, 255]),
                                f"Center pixel of webcam overlay incorrect for {position_name}")

                # Check a pixel on the main frame that should *not* have been affected
                # Pick a point clearly outside any potential overlay position
                if position_name == 'top-left':
                    # If top-left, check bottom-right of main frame
                    self.assertTrue(np.array_equal(result_frame[self.main_frame_height - 1, self.main_frame_width - 1], [0, 0, 0]),
                                    f"Unaffected pixel changed for {position_name}")
                elif position_name == 'bottom-right':
                     # If bottom-right, check top-left of main frame
                    self.assertTrue(np.array_equal(result_frame[0,0], [0,0,0]),
                                    f"Unaffected pixel changed for {position_name}")
                else:
                    # For other cases, check a pixel known to be outside
                    # e.g. if not top-left, (0,0) should be black. If not bottom-right etc.
                    # A simple check: if overlay is not at (0,0), then (0,0) should be black.
                    if start_y != 0 or start_x != 0:
                         self.assertTrue(np.array_equal(result_frame[0,0], [0,0,0]),
                                    f"Unaffected pixel (0,0) changed for {position_name}")
                    # If overlay is not at bottom right, then bottom right of main frame should be black
                    if start_y + self.webcam_frame_height != self.main_frame_height or \
                       start_x + self.webcam_frame_width != self.main_frame_width:
                         self.assertTrue(np.array_equal(result_frame[self.main_frame_height-1, self.main_frame_width-1], [0,0,0]),
                                    f"Unaffected pixel (bottom-right) changed for {position_name}")


    def test_overlay_webcam_invalid_position(self):
        """Test overlay_webcam with an invalid position string."""
        current_main_frame = self.main_frame.copy()
        # Expect it to default to 'top-right' or handle error gracefully, 
        # current implementation defaults to 'top-right' if position is unknown
        result_frame = overlay_webcam(current_main_frame, self.webcam_frame, "invalid-position")
        self.assertIsNotNone(result_frame)
        # Check if it defaulted to top-right
        start_y, start_x = 0, self.main_frame_width - self.webcam_frame_width
        self.assertTrue(np.array_equal(result_frame[start_y, start_x], [255, 255, 255]),
                        "Default overlay for invalid position did not seem to be top-right.")

if __name__ == '__main__':
    unittest.main()
