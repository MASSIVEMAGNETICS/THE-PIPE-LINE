"""
Video Generator for the music video generation pipeline.

This module handles the actual generation and composition of video content:
- Frame generation using AI models
- Video composition and editing
- Audio synchronization
- Final video encoding
"""

import logging
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ai_orchestrator import AIOrchestrator, VideoScript
from .input_handlers import PipelineInputs

logger = logging.getLogger(__name__)


@dataclass
class VideoFrame:
    """Represents a single video frame."""
    
    frame_number: int
    timestamp: float
    image_path: Optional[str] = None
    scene_id: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert frame to dictionary."""
        return {
            "frame_number": self.frame_number,
            "timestamp": self.timestamp,
            "image_path": self.image_path,
            "scene_id": self.scene_id
        }


@dataclass
class GenerationProgress:
    """Track video generation progress."""
    
    total_frames: int = 0
    generated_frames: int = 0
    current_scene: int = 0
    total_scenes: int = 0
    status: str = "pending"
    errors: List[str] = field(default_factory=list)
    
    @property
    def percentage(self) -> float:
        """Get completion percentage."""
        if self.total_frames == 0:
            return 0.0
        return (self.generated_frames / self.total_frames) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert progress to dictionary."""
        return {
            "total_frames": self.total_frames,
            "generated_frames": self.generated_frames,
            "current_scene": self.current_scene,
            "total_scenes": self.total_scenes,
            "status": self.status,
            "percentage": self.percentage,
            "errors": self.errors
        }


class VideoGenerator:
    """
    Video Generator that creates and composes music video content.
    
    This class takes the orchestrated plan and generates the actual video
    frames, composes them with audio, and outputs the final MP4.
    """
    
    def __init__(self, 
                 inputs: PipelineInputs,
                 video_script: VideoScript,
                 output_dir: str,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Video Generator.
        
        Args:
            inputs: PipelineInputs containing all user inputs
            video_script: VideoScript from the AI orchestrator
            output_dir: Directory for output files
            config: Optional configuration dictionary
        """
        self.inputs = inputs
        self.video_script = video_script
        self.output_dir = Path(output_dir)
        self.config = config or {}
        
        # Configuration
        self.fps = self.config.get("fps", 30)
        self.resolution = self.config.get("resolution", (1920, 1080))
        self.quality = self.config.get("quality", "high")
        
        # State
        self.progress = GenerationProgress()
        self.frames: List[VideoFrame] = []
        self.temp_dir: Optional[Path] = None
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def setup(self) -> bool:
        """Set up the generation environment."""
        logger.info("Setting up video generation environment...")
        
        # Create temporary directory for frames
        self.temp_dir = self.output_dir / "temp_frames"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Calculate total frames
        total_duration = self.video_script.total_duration
        self.progress.total_frames = int(total_duration * self.fps)
        self.progress.total_scenes = len(self.video_script.scenes)
        self.progress.status = "setup_complete"
        
        logger.info(f"Setup complete: {self.progress.total_frames} frames to generate")
        return True
    
    def generate_frame(self, frame_number: int, scene_id: int) -> VideoFrame:
        """
        Generate a single video frame.
        
        In production, this would call AI image generation APIs.
        
        Args:
            frame_number: Frame number
            scene_id: Current scene ID
            
        Returns:
            Generated VideoFrame
        """
        timestamp = frame_number / self.fps
        
        # Create placeholder frame (in production, use AI generation)
        frame = VideoFrame(
            frame_number=frame_number,
            timestamp=timestamp,
            scene_id=scene_id
        )
        
        return frame
    
    def generate_all_frames(self) -> bool:
        """
        Generate all frames for the video.
        
        Returns:
            True if all frames generated successfully
        """
        logger.info("Starting frame generation...")
        self.progress.status = "generating"
        
        frame_number = 0
        
        for scene in self.video_script.scenes:
            self.progress.current_scene = scene.scene_id
            scene_start_frame = int(scene.start_time * self.fps)
            scene_end_frame = int(scene.end_time * self.fps)
            
            logger.info(f"Generating frames for scene {scene.scene_id} "
                       f"({scene_start_frame}-{scene_end_frame})")
            
            for frame_num in range(scene_start_frame, scene_end_frame):
                try:
                    frame = self.generate_frame(frame_num, scene.scene_id)
                    self.frames.append(frame)
                    self.progress.generated_frames += 1
                except Exception as e:
                    error_msg = f"Error generating frame {frame_num}: {str(e)}"
                    logger.error(error_msg)
                    self.progress.errors.append(error_msg)
        
        self.progress.status = "frames_complete"
        logger.info(f"Frame generation complete: {len(self.frames)} frames")
        return len(self.progress.errors) == 0
    
    def compose_video(self, output_filename: str = "music_video.mp4") -> str:
        """
        Compose all frames into a video file.
        
        Args:
            output_filename: Name of the output file
            
        Returns:
            Path to the composed video
        """
        logger.info("Composing video from frames...")
        self.progress.status = "composing"
        
        output_path = self.output_dir / output_filename
        
        # In production, use ffmpeg or moviepy to compose frames
        # For now, create a placeholder
        composition_info = {
            "total_frames": len(self.frames),
            "fps": self.fps,
            "resolution": self.resolution,
            "duration": self.video_script.total_duration,
            "scenes": len(self.video_script.scenes)
        }
        
        logger.info(f"Video composition info: {composition_info}")
        
        # Create output file (placeholder for actual video generation)
        output_path.touch()
        
        self.progress.status = "video_composed"
        return str(output_path)
    
    def add_audio(self, video_path: str, output_filename: str = "music_video_with_audio.mp4") -> str:
        """
        Add audio track to the composed video.
        
        Args:
            video_path: Path to the video without audio
            output_filename: Name of the output file with audio
            
        Returns:
            Path to the final video with audio
        """
        logger.info("Adding audio to video...")
        self.progress.status = "adding_audio"
        
        output_path = self.output_dir / output_filename
        
        if self.inputs.audio.file_path:
            audio_path = self.inputs.audio.file_path
            logger.info(f"Adding audio from: {audio_path}")
            
            # In production, use ffmpeg to merge audio and video
            # ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac output.mp4
        
        # Create output file (placeholder)
        shutil.copy(video_path, output_path)
        
        self.progress.status = "audio_added"
        return str(output_path)
    
    def apply_lip_sync(self, video_path: str) -> str:
        """
        Apply lip sync effects if lyrics are available.
        
        Args:
            video_path: Path to the video
            
        Returns:
            Path to the video with lip sync applied
        """
        if not self.inputs.lyrics.has_lyrics():
            logger.info("No lyrics provided, skipping lip sync")
            return video_path
        
        logger.info("Applying lip sync effects...")
        self.progress.status = "applying_lip_sync"
        
        # In production, use Wav2Lip or similar for lip sync
        if self.inputs.lyrics.timestamps:
            logger.info("Using timestamped lyrics for precise lip sync")
        
        self.progress.status = "lip_sync_applied"
        return video_path
    
    def encode_final(self, video_path: str, output_filename: str = "final_music_video.mp4") -> str:
        """
        Encode the final video with optimal settings.
        
        Args:
            video_path: Path to the video to encode
            output_filename: Name of the final output file
            
        Returns:
            Path to the final encoded video
        """
        logger.info("Encoding final video...")
        self.progress.status = "encoding"
        
        output_path = self.output_dir / output_filename
        
        # Encoding settings based on quality
        encoding_settings = {
            "low": {"crf": 28, "preset": "fast"},
            "medium": {"crf": 23, "preset": "medium"},
            "high": {"crf": 18, "preset": "slow"}
        }
        
        settings = encoding_settings.get(self.quality, encoding_settings["high"])
        logger.info(f"Encoding with settings: {settings}")
        
        # In production, use ffmpeg for final encoding
        # ffmpeg -i input.mp4 -c:v libx264 -crf {crf} -preset {preset} output.mp4
        
        shutil.copy(video_path, output_path)
        
        self.progress.status = "complete"
        return str(output_path)
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        logger.info("Cleaning up temporary files...")
        
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        
        logger.info("Cleanup complete")
    
    def generate(self, output_filename: str = "music_video.mp4") -> str:
        """
        Main generation method that runs the complete video generation pipeline.
        
        Args:
            output_filename: Name of the final output file
            
        Returns:
            Path to the generated video
        """
        try:
            # Setup
            self.setup()
            
            # Generate frames
            self.generate_all_frames()
            
            # Compose video
            video_path = self.compose_video("temp_video.mp4")
            
            # Add audio
            video_with_audio = self.add_audio(video_path, "temp_with_audio.mp4")
            
            # Apply lip sync
            video_with_sync = self.apply_lip_sync(video_with_audio)
            
            # Final encoding
            final_path = self.encode_final(video_with_sync, output_filename)
            
            logger.info(f"Video generation complete: {final_path}")
            return final_path
            
        finally:
            # Cleanup
            self.cleanup()
    
    def get_progress(self) -> GenerationProgress:
        """Get current generation progress."""
        return self.progress
