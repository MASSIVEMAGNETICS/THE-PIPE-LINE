"""Export and save module for final MP4 video output.

This module handles the final rendering and export of the music video
to MP4 format, including assembly of all scenes and encoding.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
import os
import shutil

from .video_generator import VideoGenerationResult


class ExportStatus(Enum):
    """Status of the export process."""
    PENDING = "pending"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExportResult:
    """Result from the video export process.
    
    Attributes:
        status: Current status of export.
        output_path: Path to the exported MP4 file.
        file_size_bytes: Size of the exported file in bytes.
        duration_seconds: Duration of the exported video.
        error_message: Error message if export failed.
    """
    status: ExportStatus
    output_path: Optional[str] = None
    file_size_bytes: int = 0
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    
    def is_successful(self) -> bool:
        """Check if export completed successfully.
        
        Returns:
            True if status is COMPLETED and output path exists.
        """
        if self.status != ExportStatus.COMPLETED:
            return False
        if not self.output_path:
            return False
        return Path(self.output_path).exists()


class VideoExporter:
    """Exporter for final music video to MP4 format.
    
    This class handles assembly of rendered scenes and export
    to the final MP4 file format.
    """
    
    DEFAULT_BITRATE = "5M"
    DEFAULT_CODEC = "h264"
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        bitrate: str = DEFAULT_BITRATE,
        codec: str = DEFAULT_CODEC
    ) -> None:
        """Initialize the video exporter.
        
        Args:
            output_dir: Directory for output files.
            bitrate: Video bitrate for encoding.
            codec: Video codec to use.
        """
        self.output_dir = output_dir or os.getcwd()
        self.bitrate = bitrate
        self.codec = codec
    
    def export(
        self,
        generation_result: VideoGenerationResult,
        output_filename: str = "music_video.mp4"
    ) -> ExportResult:
        """Export the generated video to MP4 format.
        
        Args:
            generation_result: Result from video generation.
            output_filename: Name for the output MP4 file.
            
        Returns:
            ExportResult with path to exported file.
        """
        if not generation_result.is_successful():
            return ExportResult(
                status=ExportStatus.FAILED,
                error_message="Cannot export from failed video generation"
            )
        
        try:
            # Ensure output directory exists
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            
            output_path = Path(self.output_dir) / output_filename
            
            # Assemble scenes and create final video
            duration = self._assemble_video(
                generation_result.rendered_scenes,
                output_path,
                generation_result.fps,
                generation_result.resolution
            )
            
            # Get file size
            file_size = output_path.stat().st_size if output_path.exists() else 0
            
            return ExportResult(
                status=ExportStatus.COMPLETED,
                output_path=str(output_path),
                file_size_bytes=file_size,
                duration_seconds=duration
            )
            
        except Exception as e:
            return ExportResult(
                status=ExportStatus.FAILED,
                error_message=str(e)
            )
    
    def _assemble_video(
        self,
        rendered_scenes: list,
        output_path: Path,
        fps: int,
        resolution: tuple[int, int]
    ) -> float:
        """Assemble all scenes into final video file.
        
        In production, this would use a video encoding library like
        ffmpeg to properly encode all frames into an MP4 file.
        For now, it creates a placeholder MP4 file structure.
        
        Args:
            rendered_scenes: List of rendered scene data.
            output_path: Path for output MP4 file.
            fps: Frames per second.
            resolution: Video resolution.
            
        Returns:
            Total duration of assembled video in seconds.
        """
        total_duration = sum(scene.duration_seconds for scene in rendered_scenes)
        
        # Create a placeholder MP4 file
        # In production, this would use proper video encoding
        self._create_placeholder_mp4(
            output_path,
            rendered_scenes,
            fps,
            resolution,
            total_duration
        )
        
        return total_duration
    
    def _create_placeholder_mp4(
        self,
        output_path: Path,
        rendered_scenes: list,
        fps: int,
        resolution: tuple[int, int],
        duration: float
    ) -> None:
        """Create a placeholder MP4 file structure.
        
        This creates a valid file that represents the final video output.
        In production, this would be replaced with actual MP4 encoding.
        
        Args:
            output_path: Path for the MP4 file.
            rendered_scenes: Scene data to include.
            fps: Frames per second.
            resolution: Video resolution.
            duration: Total duration.
        """
        # Create MP4 file header structure
        # This is a minimal valid MP4 file structure (ftyp box)
        mp4_header = bytes([
            # ftyp box (file type)
            0x00, 0x00, 0x00, 0x1C,  # box size (28 bytes)
            0x66, 0x74, 0x79, 0x70,  # 'ftyp'
            0x69, 0x73, 0x6F, 0x6D,  # 'isom' (major brand)
            0x00, 0x00, 0x02, 0x00,  # minor version
            0x69, 0x73, 0x6F, 0x6D,  # 'isom' (compatible brand)
            0x69, 0x73, 0x6F, 0x32,  # 'iso2' (compatible brand)
            0x6D, 0x70, 0x34, 0x31,  # 'mp41' (compatible brand)
        ])
        
        # Write the placeholder MP4 file
        with open(output_path, "wb") as f:
            f.write(mp4_header)
            
            # Add metadata as comment (mdat box placeholder)
            metadata = (
                f"\n# Music Video Pipeline Output\n"
                f"# Resolution: {resolution[0]}x{resolution[1]}\n"
                f"# FPS: {fps}\n"
                f"# Duration: {duration}s\n"
                f"# Scenes: {len(rendered_scenes)}\n"
                f"# Codec: {self.codec}\n"
                f"# Bitrate: {self.bitrate}\n"
            ).encode('utf-8')
            
            f.write(metadata)
    
    def save_to_path(self, export_result: ExportResult, destination: str) -> bool:
        """Save the exported video to a specific destination.
        
        Args:
            export_result: Result from export operation.
            destination: Destination path for the video.
            
        Returns:
            True if save was successful, False otherwise.
        """
        if not export_result.is_successful():
            return False
        
        try:
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(export_result.output_path, dest_path)
            return True
        except Exception:
            return False
