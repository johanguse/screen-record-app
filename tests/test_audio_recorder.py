import unittest
from screen_record_app.recording.audio_recorder import AudioRecorder

class TestAudioRecorder(unittest.TestCase):
    def setUp(self):
        """Set up for test methods."""
        self.recorder = AudioRecorder()

    def test_get_audio_data_retrieves_and_clears_data(self):
        """Test that get_audio_data retrieves concatenated data and clears the internal list."""
        sample_data = [b'chunk1', b'chunk2', b'chunk3']
        expected_joined_data = b'chunk1chunk2chunk3'
        
        # Manually populate audio_data for testing
        self.recorder.audio_data = list(sample_data) # Use a copy
        
        retrieved_data = self.recorder.get_audio_data()
        
        self.assertEqual(retrieved_data, expected_joined_data, "Retrieved data does not match expected joined data.")
        self.assertEqual(self.recorder.audio_data, [], "audio_data list was not cleared after get_audio_data.")

    def test_get_audio_data_empty(self):
        """Test get_audio_data when audio_data is initially empty."""
        # audio_data is already empty by default from setUp or __init__
        retrieved_data = self.recorder.get_audio_data()
        
        self.assertEqual(retrieved_data, b'', "Retrieved data should be empty bytes if audio_data was empty.")
        self.assertEqual(self.recorder.audio_data, [], "audio_data list should remain empty.")

    def test_clear_audio_data(self):
        """Test that clear_audio_data correctly empties the audio_data list."""
        # Manually populate audio_data for testing
        self.recorder.audio_data = [b'some_data']
        
        self.recorder.clear_audio_data()
        
        self.assertEqual(self.recorder.audio_data, [], "audio_data list was not cleared by clear_audio_data.")

if __name__ == '__main__':
    unittest.main()
