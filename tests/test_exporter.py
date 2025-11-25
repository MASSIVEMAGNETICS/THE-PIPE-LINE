"""Tests for video export module."""

import pytest
import tempfile
from pathlib import Path

from pipeline.video_generator import (
    VideoGenerationResult,
    RenderStatus,
    RenderedScene,
)
from pipeline.exporter import (
    VideoExporter,
    ExportResult,
    ExportStatus,
)


class TestExportResult:
    """Tests for ExportResult dataclass."""
    
    def test_successful_result_with_file(self, tmp_path):
        """Successful result with existing file should return is_successful True."""
        # Create a test file
        output_file = tmp_path / "test.mp4"
        output_file.write_bytes(b"test content")
        
        result = ExportResult(
            status=ExportStatus.COMPLETED,
            output_path=str(output_file),
            file_size_bytes=12,
            duration_seconds=60.0
        )
        
        assert result.is_successful() is True
    
    def test_successful_result_without_file(self):
        """Successful result without file should return is_successful False."""
        result = ExportResult(
            status=ExportStatus.COMPLETED,
            output_path="/nonexistent/file.mp4"
        )
        
        assert result.is_successful() is False
    
    def test_failed_result(self):
        """Failed result should return is_successful False."""
        result = ExportResult(
            status=ExportStatus.FAILED,
            error_message="Export failed"
        )
        
        assert result.is_successful() is False


class TestVideoExporter:
    """Tests for VideoExporter class."""
    
    @pytest.fixture
    def exporter(self, tmp_path):
        """Create an exporter instance with temp output dir."""
        return VideoExporter(output_dir=str(tmp_path))
    
    @pytest.fixture
    def successful_generation(self):
        """Create a successful generation result."""
        scenes = [
            RenderedScene(
                scene_id=1,
                frame_count=150,
                duration_seconds=5.0,
                temp_path="/tmp/scene_1"
            ),
            RenderedScene(
                scene_id=2,
                frame_count=150,
                duration_seconds=5.0,
                temp_path="/tmp/scene_2"
            ),
        ]
        
        return VideoGenerationResult(
            status=RenderStatus.COMPLETED,
            rendered_scenes=scenes,
            total_frames=300,
            resolution=(1920, 1080),
            fps=30
        )
    
    @pytest.fixture
    def failed_generation(self):
        """Create a failed generation result."""
        return VideoGenerationResult(
            status=RenderStatus.FAILED,
            error_message="Generation failed"
        )
    
    def test_export_successful_generation(self, exporter, successful_generation, tmp_path):
        """Should export from successful generation."""
        result = exporter.export(successful_generation, "output.mp4")
        
        assert result.status == ExportStatus.COMPLETED
        assert result.is_successful()
        assert result.output_path is not None
        assert Path(result.output_path).exists()
    
    def test_export_failed_generation(self, exporter, failed_generation):
        """Should fail when generation failed."""
        result = exporter.export(failed_generation, "output.mp4")
        
        assert result.status == ExportStatus.FAILED
        assert not result.is_successful()
        assert "failed video generation" in result.error_message.lower()
    
    def test_export_creates_mp4_file(self, exporter, successful_generation, tmp_path):
        """Exported file should be an MP4."""
        result = exporter.export(successful_generation, "test_video.mp4")
        
        assert result.output_path.endswith(".mp4")
        assert Path(result.output_path).exists()
    
    def test_export_file_has_content(self, exporter, successful_generation):
        """Exported file should have content."""
        result = exporter.export(successful_generation, "output.mp4")
        
        assert result.file_size_bytes > 0
    
    def test_export_duration_calculated(self, exporter, successful_generation):
        """Duration should be calculated from scenes."""
        result = exporter.export(successful_generation, "output.mp4")
        
        expected_duration = sum(
            scene.duration_seconds 
            for scene in successful_generation.rendered_scenes
        )
        
        assert result.duration_seconds == expected_duration
    
    def test_save_to_path(self, exporter, successful_generation, tmp_path):
        """Should save exported video to specific path."""
        result = exporter.export(successful_generation, "output.mp4")
        
        dest_path = tmp_path / "saved" / "my_video.mp4"
        success = exporter.save_to_path(result, str(dest_path))
        
        assert success
        assert dest_path.exists()
    
    def test_save_to_path_failed_export(self, exporter, failed_generation, tmp_path):
        """Should return False when saving failed export."""
        result = exporter.export(failed_generation, "output.mp4")
        
        dest_path = tmp_path / "saved" / "my_video.mp4"
        success = exporter.save_to_path(result, str(dest_path))
        
        assert not success
    
    def test_custom_filename(self, exporter, successful_generation, tmp_path):
        """Should use custom filename."""
        result = exporter.export(successful_generation, "my_custom_video.mp4")
        
        assert "my_custom_video.mp4" in result.output_path
