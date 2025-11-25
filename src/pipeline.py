"""
Main Pipeline module for end-to-end music video generation.

This is the main entry point that coordinates all components:
- Input handling
- AI orchestration
- Video generation
- Export/Save
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ai_orchestrator import AIOrchestrator
from .exporter import ExportMetadata, ExportResult, VideoExporter
from .input_handlers import (
    AudioInput,
    BackgroundInput,
    CharacterInput,
    ElementInput,
    LyricsInput,
    PipelineInputs,
)
from .video_generator import GenerationProgress, VideoGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for the music video generation pipeline."""
    
    # Video settings
    fps: int = 30
    resolution: tuple = (1920, 1080)
    quality: str = "high"  # low, medium, high
    
    # Output settings
    output_dir: str = "./output"
    output_filename: str = "music_video.mp4"
    
    # Generation settings
    style: str = "cinematic"
    enable_lip_sync: bool = True
    
    # AI settings
    ai_model: str = "default"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "fps": self.fps,
            "resolution": list(self.resolution),
            "quality": self.quality,
            "output_dir": self.output_dir,
            "output_filename": self.output_filename,
            "style": self.style,
            "enable_lip_sync": self.enable_lip_sync,
            "ai_model": self.ai_model
        }


@dataclass
class PipelineResult:
    """Result of the pipeline execution."""
    
    success: bool
    output_path: Optional[str] = None
    export_result: Optional[ExportResult] = None
    generation_progress: Optional[GenerationProgress] = None
    orchestration_result: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "output_path": self.output_path,
            "export_result": self.export_result.to_dict() if self.export_result else None,
            "generation_progress": self.generation_progress.to_dict() if self.generation_progress else None,
            "errors": self.errors,
            "execution_time": self.execution_time
        }


class MusicVideoPipeline:
    """
    End-to-End Music Video Generation Pipeline.
    
    This class orchestrates the complete process of generating a music video:
    
    1. Accept user inputs:
       - Song/audio as prompt
       - Up to 5 character images (+ optional additional)
       - Up to 5 background images
       - Up to 5 element images
       - Optional lyrics for lip sync
    
    2. AI orchestration to plan the video
    
    3. Generate video content
    
    4. Export as MP4
    
    Usage:
        pipeline = MusicVideoPipeline()
        pipeline.add_audio(file_path="song.mp3")
        pipeline.add_character_image("character.png")
        pipeline.add_background_image("background.jpg")
        result = pipeline.run()
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the Music Video Pipeline.
        
        Args:
            config: Optional PipelineConfig for customization
        """
        self.config = config or PipelineConfig()
        self.inputs = PipelineInputs()
        self.orchestrator: Optional[AIOrchestrator] = None
        self.generator: Optional[VideoGenerator] = None
        self.exporter: Optional[VideoExporter] = None
        self._is_initialized = False
        self._start_time: Optional[datetime] = None
        
        logger.info("Music Video Pipeline initialized")
    
    # =========================================================================
    # INPUT METHODS
    # =========================================================================
    
    def add_audio(self, 
                  file_path: Optional[str] = None,
                  prompt_description: Optional[str] = None,
                  duration_seconds: Optional[float] = None) -> 'MusicVideoPipeline':
        """
        Add audio/song input.
        
        Args:
            file_path: Path to audio file (mp3, wav, etc.)
            prompt_description: Text description of the desired audio style
            duration_seconds: Duration of the video in seconds
            
        Returns:
            Self for method chaining
        """
        self.inputs.audio = AudioInput(
            file_path=file_path,
            prompt_description=prompt_description,
            duration_seconds=duration_seconds
        )
        logger.info(f"Audio input added: {file_path or prompt_description}")
        return self
    
    def add_character_image(self, 
                           path: str, 
                           is_additional: bool = False) -> 'MusicVideoPipeline':
        """
        Add a character image (up to 5 primary + optional additional).
        
        Args:
            path: Path to the image file
            is_additional: Whether this is an additional character image
            
        Returns:
            Self for method chaining
        """
        if is_additional:
            self.inputs.characters.add_additional_image(path)
            logger.info(f"Additional character image added: {path}")
        else:
            self.inputs.characters.add_primary_image(path)
            logger.info(f"Primary character image added: {path}")
        return self
    
    def add_character_images(self, 
                            paths: List[str], 
                            additional_paths: Optional[List[str]] = None) -> 'MusicVideoPipeline':
        """
        Add multiple character images at once.
        
        Args:
            paths: List of primary character image paths (up to 5)
            additional_paths: Optional list of additional character image paths
            
        Returns:
            Self for method chaining
        """
        for path in paths[:5]:  # Limit to 5
            self.add_character_image(path, is_additional=False)
        
        if additional_paths:
            for path in additional_paths:
                self.add_character_image(path, is_additional=True)
        
        return self
    
    def add_background_image(self, path: str) -> 'MusicVideoPipeline':
        """
        Add a background image (up to 5).
        
        Args:
            path: Path to the background image
            
        Returns:
            Self for method chaining
        """
        self.inputs.backgrounds.add_image(path)
        logger.info(f"Background image added: {path}")
        return self
    
    def add_background_images(self, paths: List[str]) -> 'MusicVideoPipeline':
        """
        Add multiple background images at once.
        
        Args:
            paths: List of background image paths (up to 5)
            
        Returns:
            Self for method chaining
        """
        for path in paths[:5]:  # Limit to 5
            self.add_background_image(path)
        return self
    
    def add_element_image(self, path: str) -> 'MusicVideoPipeline':
        """
        Add a video element image (up to 5).
        
        Args:
            path: Path to the element image
            
        Returns:
            Self for method chaining
        """
        self.inputs.elements.add_image(path)
        logger.info(f"Element image added: {path}")
        return self
    
    def add_element_images(self, paths: List[str]) -> 'MusicVideoPipeline':
        """
        Add multiple element images at once.
        
        Args:
            paths: List of element image paths (up to 5)
            
        Returns:
            Self for method chaining
        """
        for path in paths[:5]:  # Limit to 5
            self.add_element_image(path)
        return self
    
    def add_lyrics(self, 
                   text: Optional[str] = None,
                   file_path: Optional[str] = None,
                   timestamps: Optional[List[Dict[str, Any]]] = None) -> 'MusicVideoPipeline':
        """
        Add lyrics for lip sync (optional).
        
        Args:
            text: Lyrics as text string
            file_path: Path to lyrics file
            timestamps: Optional list of timed lyrics for precise lip sync
            
        Returns:
            Self for method chaining
        """
        if text:
            self.inputs.lyrics.set_lyrics(text)
            logger.info("Lyrics added from text")
        elif file_path:
            self.inputs.lyrics.load_from_file(file_path)
            logger.info(f"Lyrics loaded from: {file_path}")
        
        if timestamps:
            self.inputs.lyrics.set_timestamps(timestamps)
            logger.info("Timed lyrics added for lip sync")
        
        return self
    
    # =========================================================================
    # PIPELINE EXECUTION
    # =========================================================================
    
    def validate_inputs(self) -> bool:
        """
        Validate all inputs before running the pipeline.
        
        Returns:
            True if all inputs are valid
        """
        logger.info("Validating pipeline inputs...")
        
        try:
            self.inputs.validate_all()
            logger.info("All inputs validated successfully")
            return True
        except Exception as e:
            logger.error(f"Input validation failed: {str(e)}")
            raise
    
    def run(self, 
            output_filename: Optional[str] = None,
            metadata: Optional[ExportMetadata] = None) -> PipelineResult:
        """
        Run the complete music video generation pipeline.
        
        Args:
            output_filename: Custom output filename (optional)
            metadata: Optional metadata to embed in the video
            
        Returns:
            PipelineResult with details of the generation
        """
        self._start_time = datetime.now()
        result = PipelineResult(success=False)
        
        try:
            logger.info("="*60)
            logger.info("STARTING MUSIC VIDEO GENERATION PIPELINE")
            logger.info("="*60)
            
            # Step 1: Validate inputs
            self.validate_inputs()
            
            # Step 2: Initialize AI Orchestrator
            logger.info("Initializing AI Orchestrator...")
            self.orchestrator = AIOrchestrator(
                inputs=self.inputs,
                config=self.config.to_dict()
            )
            
            # Step 3: Orchestrate - plan the video
            logger.info("Running AI orchestration...")
            orchestration_result = self.orchestrator.orchestrate()
            result.orchestration_result = orchestration_result
            
            # Step 4: Initialize Video Generator
            logger.info("Initializing Video Generator...")
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            self.generator = VideoGenerator(
                inputs=self.inputs,
                video_script=self.orchestrator.get_video_script(),
                output_dir=str(output_dir),
                config=self.config.to_dict()
            )
            
            # Step 5: Generate video
            logger.info("Generating video...")
            video_path = self.generator.generate(
                output_filename=output_filename or "temp_output.mp4"
            )
            result.generation_progress = self.generator.get_progress()
            
            # Step 6: Export/Save
            logger.info("Exporting video...")
            self.exporter = VideoExporter(
                output_dir=str(output_dir),
                config=self.config.to_dict()
            )
            
            final_filename = output_filename or self.config.output_filename
            export_result = self.exporter.export(
                source_path=video_path,
                filename=Path(final_filename).stem,
                format_ext="mp4",
                metadata=metadata
            )
            
            result.export_result = export_result
            result.output_path = export_result.file_path
            result.success = export_result.success
            
            logger.info("="*60)
            logger.info("PIPELINE COMPLETE")
            logger.info(f"Output: {result.output_path}")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            result.errors.append(str(e))
            result.success = False
        
        finally:
            # Calculate execution time
            if self._start_time:
                result.execution_time = (datetime.now() - self._start_time).total_seconds()
        
        return result
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_input_summary(self) -> Dict[str, Any]:
        """Get a summary of current inputs."""
        return self.inputs.get_summary()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.to_dict()
    
    def set_config(self, **kwargs) -> 'MusicVideoPipeline':
        """
        Update configuration settings.
        
        Args:
            **kwargs: Configuration key-value pairs
            
        Returns:
            Self for method chaining
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Config updated: {key} = {value}")
        return self
    
    def reset(self) -> 'MusicVideoPipeline':
        """
        Reset the pipeline to initial state.
        
        Returns:
            Self for method chaining
        """
        self.inputs = PipelineInputs()
        self.orchestrator = None
        self.generator = None
        self.exporter = None
        self._is_initialized = False
        logger.info("Pipeline reset to initial state")
        return self


def create_pipeline(config: Optional[Dict[str, Any]] = None) -> MusicVideoPipeline:
    """
    Factory function to create a configured pipeline.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured MusicVideoPipeline instance
    """
    pipeline_config = None
    
    if config:
        pipeline_config = PipelineConfig(
            fps=config.get("fps", 30),
            resolution=tuple(config.get("resolution", [1920, 1080])),
            quality=config.get("quality", "high"),
            output_dir=config.get("output_dir", "./output"),
            output_filename=config.get("output_filename", "music_video.mp4"),
            style=config.get("style", "cinematic"),
            enable_lip_sync=config.get("enable_lip_sync", True),
            ai_model=config.get("ai_model", "default")
        )
    
    return MusicVideoPipeline(config=pipeline_config)


# Convenience function for quick usage
def generate_music_video(
    audio_file: Optional[str] = None,
    audio_prompt: Optional[str] = None,
    character_images: Optional[List[str]] = None,
    additional_character_images: Optional[List[str]] = None,
    background_images: Optional[List[str]] = None,
    element_images: Optional[List[str]] = None,
    lyrics: Optional[str] = None,
    lyrics_file: Optional[str] = None,
    output_path: str = "./output",
    output_filename: str = "music_video.mp4",
    **config_kwargs
) -> PipelineResult:
    """
    Convenience function to generate a music video with minimal setup.
    
    Args:
        audio_file: Path to audio file
        audio_prompt: Text description of audio style
        character_images: List of character image paths (up to 5)
        additional_character_images: List of additional character images
        background_images: List of background image paths (up to 5)
        element_images: List of element image paths (up to 5)
        lyrics: Lyrics text for lip sync
        lyrics_file: Path to lyrics file
        output_path: Output directory
        output_filename: Output filename
        **config_kwargs: Additional configuration options
        
    Returns:
        PipelineResult with generation details
    """
    # Create pipeline with config
    config = {
        "output_dir": output_path,
        "output_filename": output_filename,
        **config_kwargs
    }
    pipeline = create_pipeline(config)
    
    # Add audio
    if audio_file or audio_prompt:
        pipeline.add_audio(file_path=audio_file, prompt_description=audio_prompt)
    
    # Add character images
    if character_images:
        pipeline.add_character_images(character_images, additional_character_images)
    
    # Add background images
    if background_images:
        pipeline.add_background_images(background_images)
    
    # Add element images
    if element_images:
        pipeline.add_element_images(element_images)
    
    # Add lyrics
    if lyrics or lyrics_file:
        pipeline.add_lyrics(text=lyrics, file_path=lyrics_file)
    
    # Run pipeline
    return pipeline.run(output_filename=output_filename)
