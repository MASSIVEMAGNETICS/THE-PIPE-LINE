"""
Input handlers for the music video generation pipeline.

This module provides classes to handle various types of inputs:
- Audio/Song files
- Character images
- Background images
- Video element images
- Lyrics text
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class AudioInput:
    """Handler for song/audio input."""
    
    file_path: Optional[str] = None
    prompt_description: Optional[str] = None
    duration_seconds: Optional[float] = None
    
    def validate(self) -> bool:
        """Validate the audio input."""
        if self.file_path:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"Audio file not found: {self.file_path}")
            valid_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
            ext = Path(self.file_path).suffix.lower()
            if ext not in valid_extensions:
                raise ValueError(f"Unsupported audio format: {ext}. Supported: {valid_extensions}")
        elif not self.prompt_description:
            raise ValueError("Either file_path or prompt_description must be provided")
        return True
    
    def get_duration(self) -> Optional[float]:
        """Get the duration of the audio file if available."""
        return self.duration_seconds


@dataclass
class ImageInput:
    """Handler for image inputs (characters, backgrounds, elements)."""
    
    image_paths: List[str] = field(default_factory=list)
    max_images: int = 5
    category: str = "generic"
    
    def add_image(self, path: str) -> bool:
        """Add an image to the input list."""
        if len(self.image_paths) >= self.max_images:
            raise ValueError(f"Maximum of {self.max_images} images allowed for {self.category}")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")
        
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        ext = Path(path).suffix.lower()
        if ext not in valid_extensions:
            raise ValueError(f"Unsupported image format: {ext}. Supported: {valid_extensions}")
        
        self.image_paths.append(path)
        return True
    
    def validate(self) -> bool:
        """Validate all image inputs."""
        for path in self.image_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image file not found: {path}")
        return True
    
    def get_images(self) -> List[str]:
        """Get list of image paths."""
        return self.image_paths.copy()


@dataclass
class CharacterInput:
    """Handler for character image inputs."""
    
    primary_images: ImageInput = field(default_factory=lambda: ImageInput(max_images=5, category="character"))
    additional_images: ImageInput = field(default_factory=lambda: ImageInput(max_images=10, category="additional_character"))
    
    def add_primary_image(self, path: str) -> bool:
        """Add a primary character image."""
        return self.primary_images.add_image(path)
    
    def add_additional_image(self, path: str) -> bool:
        """Add an additional character image (optional)."""
        return self.additional_images.add_image(path)
    
    def validate(self) -> bool:
        """Validate character inputs."""
        self.primary_images.validate()
        self.additional_images.validate()
        return True
    
    def get_all_images(self) -> List[str]:
        """Get all character images."""
        return self.primary_images.get_images() + self.additional_images.get_images()


@dataclass
class BackgroundInput:
    """Handler for background image inputs."""
    
    images: ImageInput = field(default_factory=lambda: ImageInput(max_images=5, category="background"))
    
    def add_image(self, path: str) -> bool:
        """Add a background image."""
        return self.images.add_image(path)
    
    def validate(self) -> bool:
        """Validate background inputs."""
        return self.images.validate()
    
    def get_images(self) -> List[str]:
        """Get background images."""
        return self.images.get_images()


@dataclass
class ElementInput:
    """Handler for video element image inputs."""
    
    images: ImageInput = field(default_factory=lambda: ImageInput(max_images=5, category="element"))
    
    def add_image(self, path: str) -> bool:
        """Add a video element image."""
        return self.images.add_image(path)
    
    def validate(self) -> bool:
        """Validate element inputs."""
        return self.images.validate()
    
    def get_images(self) -> List[str]:
        """Get element images."""
        return self.images.get_images()


@dataclass
class LyricsInput:
    """Handler for lyrics input (optional, for lip sync)."""
    
    lyrics_text: Optional[str] = None
    lyrics_file_path: Optional[str] = None
    timestamps: Optional[List[dict]] = None  # For timed lyrics
    
    def load_from_file(self, path: str) -> bool:
        """Load lyrics from a file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Lyrics file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            self.lyrics_text = f.read()
        self.lyrics_file_path = path
        return True
    
    def set_lyrics(self, text: str) -> None:
        """Set lyrics directly from text."""
        self.lyrics_text = text
    
    def set_timestamps(self, timestamps: List[dict]) -> None:
        """Set timed lyrics for lip sync."""
        self.timestamps = timestamps
    
    def validate(self) -> bool:
        """Validate lyrics input."""
        # Lyrics are optional, so empty is valid
        return True
    
    def get_lyrics(self) -> Optional[str]:
        """Get the lyrics text."""
        return self.lyrics_text
    
    def has_lyrics(self) -> bool:
        """Check if lyrics are available."""
        return self.lyrics_text is not None and len(self.lyrics_text.strip()) > 0


@dataclass
class PipelineInputs:
    """Container for all pipeline inputs."""
    
    audio: AudioInput = field(default_factory=AudioInput)
    characters: CharacterInput = field(default_factory=CharacterInput)
    backgrounds: BackgroundInput = field(default_factory=BackgroundInput)
    elements: ElementInput = field(default_factory=ElementInput)
    lyrics: LyricsInput = field(default_factory=LyricsInput)
    
    def validate_all(self) -> bool:
        """Validate all inputs."""
        self.audio.validate()
        self.characters.validate()
        self.backgrounds.validate()
        self.elements.validate()
        self.lyrics.validate()
        return True
    
    def get_summary(self) -> dict:
        """Get a summary of all inputs."""
        return {
            "audio": {
                "file": self.audio.file_path,
                "prompt": self.audio.prompt_description,
                "duration": self.audio.duration_seconds
            },
            "characters": {
                "primary_count": len(self.characters.primary_images.image_paths),
                "additional_count": len(self.characters.additional_images.image_paths),
                "images": self.characters.get_all_images()
            },
            "backgrounds": {
                "count": len(self.backgrounds.images.image_paths),
                "images": self.backgrounds.get_images()
            },
            "elements": {
                "count": len(self.elements.images.image_paths),
                "images": self.elements.get_images()
            },
            "lyrics": {
                "available": self.lyrics.has_lyrics(),
                "has_timestamps": self.lyrics.timestamps is not None
            }
        }
