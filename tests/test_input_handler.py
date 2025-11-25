"""Tests for input handling module."""

import pytest
import tempfile
from pathlib import Path

from pipeline.input_handler import (
    PipelineInput,
    validate_image_path,
    create_input_from_dict,
    MAX_CHARACTER_IMAGES,
    MAX_BACKGROUND_IMAGES,
    MAX_ELEMENT_IMAGES,
)


class TestValidateImagePath:
    """Tests for validate_image_path function."""
    
    def test_empty_path_returns_false(self):
        """Empty path should return False."""
        assert validate_image_path("") is False
        assert validate_image_path(None) is False
    
    def test_nonexistent_path_returns_false(self):
        """Non-existent file should return False."""
        assert validate_image_path("/nonexistent/image.jpg") is False
    
    def test_valid_image_returns_true(self):
        """Valid image file should return True."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"fake image content")
            temp_path = f.name
        
        try:
            assert validate_image_path(temp_path) is True
        finally:
            Path(temp_path).unlink()
    
    def test_valid_png_returns_true(self):
        """Valid PNG file should return True."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"fake png content")
            temp_path = f.name
        
        try:
            assert validate_image_path(temp_path) is True
        finally:
            Path(temp_path).unlink()
    
    def test_invalid_extension_returns_false(self):
        """File with invalid extension should return False."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not an image")
            temp_path = f.name
        
        try:
            assert validate_image_path(temp_path) is False
        finally:
            Path(temp_path).unlink()


class TestPipelineInput:
    """Tests for PipelineInput dataclass."""
    
    def test_valid_minimal_input(self):
        """Minimal valid input should be accepted."""
        input_data = PipelineInput(song_prompt="A happy summer song")
        assert input_data.song_prompt == "A happy summer song"
        assert input_data.character_images == []
        assert input_data.lyrics is None
    
    def test_empty_song_prompt_raises_error(self):
        """Empty song prompt should raise ValueError."""
        with pytest.raises(ValueError, match="Song prompt is required"):
            PipelineInput(song_prompt="")
    
    def test_whitespace_song_prompt_raises_error(self):
        """Whitespace-only song prompt should raise ValueError."""
        with pytest.raises(ValueError, match="Song prompt is required"):
            PipelineInput(song_prompt="   ")
    
    def test_too_many_character_images_raises_error(self):
        """More than MAX_CHARACTER_IMAGES should raise ValueError."""
        images = [f"img{i}.jpg" for i in range(MAX_CHARACTER_IMAGES + 1)]
        with pytest.raises(ValueError, match=f"Maximum {MAX_CHARACTER_IMAGES}"):
            PipelineInput(song_prompt="Test song", character_images=images)
    
    def test_too_many_background_images_raises_error(self):
        """More than MAX_BACKGROUND_IMAGES should raise ValueError."""
        images = [f"bg{i}.jpg" for i in range(MAX_BACKGROUND_IMAGES + 1)]
        with pytest.raises(ValueError, match=f"Maximum {MAX_BACKGROUND_IMAGES}"):
            PipelineInput(song_prompt="Test song", background_images=images)
    
    def test_too_many_element_images_raises_error(self):
        """More than MAX_ELEMENT_IMAGES should raise ValueError."""
        images = [f"elem{i}.jpg" for i in range(MAX_ELEMENT_IMAGES + 1)]
        with pytest.raises(ValueError, match=f"Maximum {MAX_ELEMENT_IMAGES}"):
            PipelineInput(song_prompt="Test song", element_images=images)
    
    def test_full_valid_input(self):
        """Full valid input with all fields should be accepted."""
        input_data = PipelineInput(
            song_prompt="An emotional ballad about love",
            character_images=["char1.jpg", "char2.jpg"],
            additional_character_image="extra_char.jpg",
            background_images=["bg1.jpg"],
            element_images=["prop1.jpg", "prop2.jpg"],
            lyrics="These are the lyrics\nLine 2"
        )
        
        assert input_data.song_prompt == "An emotional ballad about love"
        assert len(input_data.character_images) == 2
        assert input_data.additional_character_image == "extra_char.jpg"
        assert len(input_data.background_images) == 1
        assert len(input_data.element_images) == 2
        assert "lyrics" in input_data.lyrics.lower()
    
    def test_has_lyrics_returns_true_when_provided(self):
        """has_lyrics should return True when lyrics are provided."""
        input_data = PipelineInput(
            song_prompt="Test song",
            lyrics="Some lyrics here"
        )
        assert input_data.has_lyrics() is True
    
    def test_has_lyrics_returns_false_when_empty(self):
        """has_lyrics should return False when lyrics are empty."""
        input_data = PipelineInput(song_prompt="Test song", lyrics="")
        assert input_data.has_lyrics() is False
        
        input_data2 = PipelineInput(song_prompt="Test song", lyrics="   ")
        assert input_data2.has_lyrics() is False
    
    def test_has_lyrics_returns_false_when_none(self):
        """has_lyrics should return False when lyrics are None."""
        input_data = PipelineInput(song_prompt="Test song")
        assert input_data.has_lyrics() is False
    
    def test_get_all_images(self):
        """get_all_images should return all image paths."""
        input_data = PipelineInput(
            song_prompt="Test song",
            character_images=["char1.jpg", "char2.jpg"],
            additional_character_image="extra.jpg",
            background_images=["bg1.jpg"],
            element_images=["elem1.jpg"]
        )
        
        all_images = input_data.get_all_images()
        assert len(all_images) == 5
        assert "char1.jpg" in all_images
        assert "char2.jpg" in all_images
        assert "extra.jpg" in all_images
        assert "bg1.jpg" in all_images
        assert "elem1.jpg" in all_images


class TestCreateInputFromDict:
    """Tests for create_input_from_dict function."""
    
    def test_create_from_minimal_dict(self):
        """Should create input from minimal dictionary."""
        data = {"song_prompt": "A rock anthem"}
        input_data = create_input_from_dict(data)
        assert input_data.song_prompt == "A rock anthem"
    
    def test_create_from_full_dict(self):
        """Should create input from full dictionary."""
        data = {
            "song_prompt": "An epic song",
            "character_images": ["c1.jpg", "c2.jpg"],
            "additional_character_image": "extra.jpg",
            "background_images": ["bg.jpg"],
            "element_images": ["e1.jpg"],
            "lyrics": "Lyrics here"
        }
        
        input_data = create_input_from_dict(data)
        assert input_data.song_prompt == "An epic song"
        assert len(input_data.character_images) == 2
        assert input_data.additional_character_image == "extra.jpg"
        assert input_data.has_lyrics() is True
    
    def test_create_from_empty_song_prompt_raises_error(self):
        """Should raise error for empty song prompt."""
        with pytest.raises(ValueError):
            create_input_from_dict({"song_prompt": ""})
