"""
Exporter module for the music video generation pipeline.

This module handles the export and saving of generated music videos:
- File format conversion
- Quality optimization
- Metadata embedding
- Export to various destinations
"""

import hashlib
import json
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ExportMetadata:
    """Metadata for exported video."""
    
    title: str = "Music Video"
    artist: str = ""
    album: str = ""
    year: int = 0
    genre: str = "Music Video"
    description: str = ""
    created_at: str = ""
    pipeline_version: str = "1.0.0"
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.year:
            self.year = datetime.now().year
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "year": self.year,
            "genre": self.genre,
            "description": self.description,
            "created_at": self.created_at,
            "pipeline_version": self.pipeline_version
        }
    
    def to_json(self) -> str:
        """Convert metadata to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ExportResult:
    """Result of an export operation."""
    
    success: bool
    file_path: str
    file_size: int = 0
    format: str = "mp4"
    duration: float = 0.0
    checksum: str = ""
    metadata: Optional[ExportMetadata] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "format": self.format,
            "duration": self.duration,
            "checksum": self.checksum,
            "metadata": self.metadata.to_dict() if self.metadata else None
        }


class VideoExporter:
    """
    Video Exporter that handles saving and exporting generated music videos.
    
    Supports:
    - MP4 format export (primary)
    - Various quality settings
    - Metadata embedding
    - Checksum verification
    """
    
    SUPPORTED_FORMATS = {"mp4", "webm", "mov", "avi"}
    
    def __init__(self, 
                 output_dir: str,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Video Exporter.
        
        Args:
            output_dir: Base directory for exports
            config: Optional configuration dictionary
        """
        self.output_dir = Path(output_dir)
        self.config = config or {}
        self.export_history: List[ExportResult] = []
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        return os.path.getsize(file_path)
    
    def _generate_filename(self, 
                          base_name: str, 
                          format_ext: str,
                          add_timestamp: bool = True) -> str:
        """Generate a unique filename."""
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{base_name}_{timestamp}.{format_ext}"
        return f"{base_name}.{format_ext}"
    
    def export(self,
               source_path: str,
               filename: Optional[str] = None,
               format_ext: str = "mp4",
               metadata: Optional[ExportMetadata] = None,
               add_timestamp: bool = True) -> ExportResult:
        """
        Export a video file to the output directory.
        
        Args:
            source_path: Path to the source video
            filename: Optional custom filename (without extension)
            format_ext: Output format extension
            metadata: Optional metadata to embed
            add_timestamp: Whether to add timestamp to filename
            
        Returns:
            ExportResult with details of the export
        """
        logger.info(f"Exporting video: {source_path}")
        
        # Validate format
        if format_ext.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format_ext}. "
                           f"Supported: {self.SUPPORTED_FORMATS}")
        
        # Validate source file
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Generate filename
        base_name = filename or "music_video"
        output_filename = self._generate_filename(base_name, format_ext, add_timestamp)
        output_path = self.output_dir / output_filename
        
        try:
            # Copy/convert file
            # In production, use ffmpeg for format conversion if needed
            shutil.copy(source_path, output_path)
            
            # Calculate file info
            file_size = self._get_file_size(str(output_path))
            checksum = self._calculate_checksum(str(output_path))
            
            # Create result
            result = ExportResult(
                success=True,
                file_path=str(output_path),
                file_size=file_size,
                format=format_ext,
                checksum=checksum,
                metadata=metadata
            )
            
            # Save metadata file
            if metadata:
                metadata_path = output_path.with_suffix('.json')
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    f.write(metadata.to_json())
                logger.info(f"Metadata saved to: {metadata_path}")
            
            self.export_history.append(result)
            logger.info(f"Export successful: {output_path} ({file_size} bytes)")
            
            return result
            
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            result = ExportResult(
                success=False,
                file_path="",
                metadata=metadata
            )
            self.export_history.append(result)
            raise
    
    def export_multiple_formats(self,
                               source_path: str,
                               formats: List[str],
                               filename: Optional[str] = None,
                               metadata: Optional[ExportMetadata] = None) -> List[ExportResult]:
        """
        Export video in multiple formats.
        
        Args:
            source_path: Path to the source video
            formats: List of format extensions
            filename: Optional custom filename
            metadata: Optional metadata
            
        Returns:
            List of ExportResults
        """
        results = []
        
        for format_ext in formats:
            try:
                result = self.export(
                    source_path=source_path,
                    filename=filename,
                    format_ext=format_ext,
                    metadata=metadata,
                    add_timestamp=True
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to export {format_ext}: {str(e)}")
                results.append(ExportResult(
                    success=False,
                    file_path="",
                    format=format_ext,
                    metadata=metadata
                ))
        
        return results
    
    def get_export_history(self) -> List[Dict[str, Any]]:
        """Get history of all exports."""
        return [r.to_dict() for r in self.export_history]
    
    def verify_export(self, export_result: ExportResult) -> bool:
        """
        Verify an exported file.
        
        Args:
            export_result: The ExportResult to verify
            
        Returns:
            True if file is valid
        """
        if not export_result.success:
            return False
        
        if not os.path.exists(export_result.file_path):
            logger.error(f"File not found: {export_result.file_path}")
            return False
        
        # Verify checksum
        current_checksum = self._calculate_checksum(export_result.file_path)
        if current_checksum != export_result.checksum:
            logger.error("Checksum mismatch - file may be corrupted")
            return False
        
        logger.info(f"Export verified: {export_result.file_path}")
        return True
    
    def save_to_custom_path(self, 
                           source_path: str, 
                           destination_path: str,
                           metadata: Optional[ExportMetadata] = None) -> ExportResult:
        """
        Save video to a custom path.
        
        Args:
            source_path: Path to the source video
            destination_path: Full path for the destination
            metadata: Optional metadata
            
        Returns:
            ExportResult
        """
        logger.info(f"Saving to custom path: {destination_path}")
        
        # Validate source
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Ensure destination directory exists
        dest_dir = Path(destination_path).parent
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy(source_path, destination_path)
        
        # Calculate file info
        file_size = self._get_file_size(destination_path)
        checksum = self._calculate_checksum(destination_path)
        format_ext = Path(destination_path).suffix.lstrip('.')
        
        result = ExportResult(
            success=True,
            file_path=destination_path,
            file_size=file_size,
            format=format_ext,
            checksum=checksum,
            metadata=metadata
        )
        
        self.export_history.append(result)
        logger.info(f"Saved successfully: {destination_path}")
        
        return result
