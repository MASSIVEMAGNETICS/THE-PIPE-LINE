"""
Tests for input handlers module.
"""

import os
import tempfile
import pytest
from pathlib import Path

from src.input_handlers import (
    AudioInput,
    ImageInput,
    CharacterInput,
    BackgroundInput,
    ElementInput,
    LyricsInput,
    PipelineInputs,
)


class TestAudioInput:
    """Tests for AudioInput class."""
    
    def test_audio_input_with_prompt(self):
        """Test creating audio input with prompt description."""
        audio = AudioInput(
            prompt_description="upbeat pop song",
            duration_seconds=180.0
        )
        assert audio.validate() is True
        assert audio.prompt_description == "upbeat pop song"
        assert audio.get_duration() == 180.0
    
    def test_audio_input_with_file(self, tmp_path):
        """Test creating audio input with file path."""
        # Create a temporary audio file
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        
        audio = AudioInput(file_path=str(audio_file))
        assert audio.validate() is True
    
    def test_audio_input_invalid_extension(self, tmp_path):
        """Test audio input with invalid file extension."""
        invalid_file = tmp_path / "test.xyz"
        invalid_file.touch()
        
        audio = AudioInput(file_path=str(invalid_file))
        with pytest.raises(ValueError, match="Unsupported audio format"):
            audio.validate()
    
    def test_audio_input_file_not_found(self):
        """Test audio input with non-existent file."""
        audio = AudioInput(file_path="/nonexistent/path/audio.mp3")
        with pytest.raises(FileNotFoundError):
            audio.validate()
    
    def test_audio_input_no_input(self):
        """Test audio input with no input provided."""
        audio = AudioInput()
        with pytest.raises(ValueError, match="Either file_path or prompt_description"):
            audio.validate()


class TestImageInput:
    """Tests for ImageInput class."""
    
    def test_add_single_image(self, tmp_path):
        """Test adding a single image."""
        image_file = tmp_path / "test.png"
        image_file.touch()
        
        img_input = ImageInput(max_images=5, category="test")
        assert img_input.add_image(str(image_file)) is True
        assert len(img_input.get_images()) == 1
    
    def test_add_multiple_images(self, tmp_path):
        """Test adding multiple images."""
        img_input = ImageInput(max_images=5, category="test")
        
        for i in range(5):
            image_file = tmp_path / f"test{i}.jpg"
            image_file.touch()
            img_input.add_image(str(image_file))
        
        assert len(img_input.get_images()) == 5
    
    def test_exceed_max_images(self, tmp_path):
        """Test exceeding maximum image limit."""
        img_input = ImageInput(max_images=3, category="test")
        
        for i in range(3):
            image_file = tmp_path / f"test{i}.png"
            image_file.touch()
            img_input.add_image(str(image_file))
        
        extra_file = tmp_path / "extra.png"
        extra_file.touch()
        
        with pytest.raises(ValueError, match="Maximum of 3 images"):
            img_input.add_image(str(extra_file))
    
    def test_invalid_image_format(self, tmp_path):
        """Test adding image with invalid format."""
        invalid_file = tmp_path / "test.xyz"
        invalid_file.touch()
        
        img_input = ImageInput()
        with pytest.raises(ValueError, match="Unsupported image format"):
            img_input.add_image(str(invalid_file))


class TestCharacterInput:
    """Tests for CharacterInput class."""
    
    def test_add_primary_character(self, tmp_path):
        """Test adding primary character image."""
        image_file = tmp_path / "character.png"
        image_file.touch()
        
        char_input = CharacterInput()
        assert char_input.add_primary_image(str(image_file)) is True
        assert len(char_input.primary_images.get_images()) == 1
    
    def test_add_additional_character(self, tmp_path):
        """Test adding additional character image."""
        image_file = tmp_path / "additional.png"
        image_file.touch()
        
        char_input = CharacterInput()
        assert char_input.add_additional_image(str(image_file)) is True
        assert len(char_input.additional_images.get_images()) == 1
    
    def test_get_all_characters(self, tmp_path):
        """Test getting all character images."""
        char_input = CharacterInput()
        
        primary = tmp_path / "primary.png"
        primary.touch()
        additional = tmp_path / "additional.png"
        additional.touch()
        
        char_input.add_primary_image(str(primary))
        char_input.add_additional_image(str(additional))
        
        all_images = char_input.get_all_images()
        assert len(all_images) == 2


class TestBackgroundInput:
    """Tests for BackgroundInput class."""
    
    def test_add_background(self, tmp_path):
        """Test adding background image."""
        image_file = tmp_path / "background.jpg"
        image_file.touch()
        
        bg_input = BackgroundInput()
        assert bg_input.add_image(str(image_file)) is True
        assert len(bg_input.get_images()) == 1


class TestElementInput:
    """Tests for ElementInput class."""
    
    def test_add_element(self, tmp_path):
        """Test adding element image."""
        image_file = tmp_path / "element.png"
        image_file.touch()
        
        elem_input = ElementInput()
        assert elem_input.add_image(str(image_file)) is True
        assert len(elem_input.get_images()) == 1


class TestLyricsInput:
    """Tests for LyricsInput class."""
    
    def test_set_lyrics_text(self):
        """Test setting lyrics from text."""
        lyrics = LyricsInput()
        lyrics.set_lyrics("Hello world, this is a test song")
        
        assert lyrics.has_lyrics() is True
        assert "Hello world" in lyrics.get_lyrics()
    
    def test_load_lyrics_from_file(self, tmp_path):
        """Test loading lyrics from file."""
        lyrics_file = tmp_path / "lyrics.txt"
        lyrics_file.write_text("Verse 1: Testing lyrics\nChorus: More lyrics")
        
        lyrics = LyricsInput()
        lyrics.load_from_file(str(lyrics_file))
        
        assert lyrics.has_lyrics() is True
        assert "Verse 1" in lyrics.get_lyrics()
    
    def test_set_timestamps(self):
        """Test setting timed lyrics."""
        lyrics = LyricsInput()
        lyrics.set_lyrics("Hello")
        lyrics.set_timestamps([
            {"time": 0.0, "text": "Hello"},
            {"time": 1.5, "text": "World"}
        ])
        
        assert lyrics.timestamps is not None
        assert len(lyrics.timestamps) == 2
    
    def test_empty_lyrics_valid(self):
        """Test that empty lyrics are valid (optional)."""
        lyrics = LyricsInput()
        assert lyrics.validate() is True
        assert lyrics.has_lyrics() is False


class TestPipelineInputs:
    """Tests for PipelineInputs container."""
    
    def test_pipeline_inputs_summary(self, tmp_path):
        """Test getting pipeline inputs summary."""
        # Create test files
        audio_file = tmp_path / "audio.mp3"
        audio_file.touch()
        char_file = tmp_path / "character.png"
        char_file.touch()
        
        inputs = PipelineInputs()
        inputs.audio = AudioInput(file_path=str(audio_file))
        inputs.characters.add_primary_image(str(char_file))
        
        summary = inputs.get_summary()
        
        assert summary["audio"]["file"] == str(audio_file)
        assert summary["characters"]["primary_count"] == 1
    
    def test_validate_all_inputs(self, tmp_path):
        """Test validating all inputs."""
        audio_file = tmp_path / "audio.mp3"
        audio_file.touch()
        
        inputs = PipelineInputs()
        inputs.audio = AudioInput(file_path=str(audio_file))
        
        assert inputs.validate_all() is True
