"""Input handling module for user prompts and media files.

This module handles all input types for the music video generation pipeline:
- Song prompt (text input)
- Character images (up to 5)
- Optional additional character image
- Background images (up to 5)
- Element images for video (up to 5)
- Optional lyrics for lip syncing
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import os


MAX_CHARACTER_IMAGES = 5
MAX_BACKGROUND_IMAGES = 5
MAX_ELEMENT_IMAGES = 5


def validate_image_path(path: str) -> bool:
    """Validate that a file exists and has a valid image extension.
    
    Args:
        path: Path to the image file.
        
    Returns:
        True if path exists and has valid image extension.
    """
    if not path:
        return False
    
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    file_path = Path(path)
    
    if not file_path.exists():
        return False
        
    return file_path.suffix.lower() in valid_extensions


@dataclass
class PipelineInput:
    """Data class representing all inputs for the music video pipeline.
    
    Attributes:
        song_prompt: Text description or prompt for the song/music.
        character_images: List of paths to character reference images (max 5).
        additional_character_image: Optional path to an extra character image.
        background_images: List of paths to background reference images (max 5).
        element_images: List of paths to element/prop images for video (max 5).
        lyrics: Optional lyrics text to improve lip syncing.
    """
    song_prompt: str
    character_images: list[str] = field(default_factory=list)
    additional_character_image: Optional[str] = None
    background_images: list[str] = field(default_factory=list)
    element_images: list[str] = field(default_factory=list)
    lyrics: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate inputs after initialization."""
        if not self.song_prompt or not self.song_prompt.strip():
            raise ValueError("Song prompt is required and cannot be empty")
        
        if len(self.character_images) > MAX_CHARACTER_IMAGES:
            raise ValueError(
                f"Maximum {MAX_CHARACTER_IMAGES} character images allowed, "
                f"got {len(self.character_images)}"
            )
        
        if len(self.background_images) > MAX_BACKGROUND_IMAGES:
            raise ValueError(
                f"Maximum {MAX_BACKGROUND_IMAGES} background images allowed, "
                f"got {len(self.background_images)}"
            )
        
        if len(self.element_images) > MAX_ELEMENT_IMAGES:
            raise ValueError(
                f"Maximum {MAX_ELEMENT_IMAGES} element images allowed, "
                f"got {len(self.element_images)}"
            )
    
    def validate_all_images(self) -> list[str]:
        """Validate all image paths and return list of invalid paths.
        
        Returns:
            List of invalid image paths (empty if all valid).
        """
        invalid_paths = []
        
        for img in self.character_images:
            if not validate_image_path(img):
                invalid_paths.append(img)
        
        if self.additional_character_image:
            if not validate_image_path(self.additional_character_image):
                invalid_paths.append(self.additional_character_image)
        
        for img in self.background_images:
            if not validate_image_path(img):
                invalid_paths.append(img)
        
        for img in self.element_images:
            if not validate_image_path(img):
                invalid_paths.append(img)
        
        return invalid_paths
    
    def get_all_images(self) -> list[str]:
        """Get all image paths as a single list.
        
        Returns:
            Combined list of all image paths.
        """
        images = list(self.character_images)
        if self.additional_character_image:
            images.append(self.additional_character_image)
        images.extend(self.background_images)
        images.extend(self.element_images)
        return images
    
    def has_lyrics(self) -> bool:
        """Check if lyrics are provided.
        
        Returns:
            True if lyrics are provided and non-empty.
        """
        return bool(self.lyrics and self.lyrics.strip())


def create_input_from_dict(data: dict) -> PipelineInput:
    """Create a PipelineInput from a dictionary.
    
    Args:
        data: Dictionary containing input data.
        
    Returns:
        PipelineInput instance.
        
    Raises:
        KeyError: If required fields are missing.
        ValueError: If validation fails.
    """
    return PipelineInput(
        song_prompt=data.get("song_prompt", ""),
        character_images=data.get("character_images", []),
        additional_character_image=data.get("additional_character_image"),
        background_images=data.get("background_images", []),
        element_images=data.get("element_images", []),
        lyrics=data.get("lyrics")
    )
