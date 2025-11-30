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
"""
Tests for exporter module.
"""

import pytest
from pathlib import Path

from src.exporter import VideoExporter, ExportMetadata, ExportResult


class TestExportMetadata:
    """Tests for ExportMetadata class."""
    
    def test_metadata_creation(self):
        """Test creating export metadata."""
        metadata = ExportMetadata(
            title="My Video",
            artist="Test Artist",
            genre="Pop"
        )
        
        assert metadata.title == "My Video"
        assert metadata.artist == "Test Artist"
        assert metadata.year > 0  # Auto-set to current year
    
    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = ExportMetadata(title="Test", artist="Artist")
        
        result = metadata.to_dict()
        
        assert result["title"] == "Test"
        assert "created_at" in result
    
    def test_metadata_to_json(self):
        """Test converting metadata to JSON."""
        metadata = ExportMetadata(title="Test")
        
        json_str = metadata.to_json()
        
        assert '"title": "Test"' in json_str


class TestExportResult:
    """Tests for ExportResult class."""
    
    def test_result_creation(self):
        """Test creating export result."""
        result = ExportResult(
            success=True,
            file_path="/path/to/video.mp4",
            file_size=1024000,
            format="mp4"
        )
        
        assert result.success is True
        assert result.file_size == 1024000
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        metadata = ExportMetadata(title="Test")
        result = ExportResult(
            success=True,
            file_path="/path/to/video.mp4",
            metadata=metadata
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["success"] is True
        assert result_dict["metadata"]["title"] == "Test"


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
    def source_video(self, tmp_path):
        """Create a source video file for testing."""
        video_file = tmp_path / "source" / "video.mp4"
        video_file.parent.mkdir(parents=True, exist_ok=True)
        video_file.write_bytes(b"fake video content for testing")
        return str(video_file)
    
    def test_exporter_creation(self, tmp_path):
        """Test creating an exporter."""
        exporter = VideoExporter(output_dir=str(tmp_path / "output"))
        
        assert exporter.output_dir.exists()
    
    def test_export_video(self, tmp_path, source_video):
        """Test exporting a video."""
        output_dir = tmp_path / "output"
        exporter = VideoExporter(output_dir=str(output_dir))
        
        result = exporter.export(
            source_path=source_video,
            filename="test_video",
            format_ext="mp4"
        )
        
        assert result.success is True
        assert Path(result.file_path).exists()
        assert result.checksum != ""
    
    def test_export_with_metadata(self, tmp_path, source_video):
        """Test exporting with metadata."""
        output_dir = tmp_path / "output"
        exporter = VideoExporter(output_dir=str(output_dir))
        
        metadata = ExportMetadata(title="Test Video", artist="Test Artist")
        
        result = exporter.export(
            source_path=source_video,
            filename="test_video",
            metadata=metadata
        )
        
        assert result.success is True
        assert result.metadata is not None
        
        # Check metadata file was created
        metadata_path = Path(result.file_path).with_suffix('.json')
        assert metadata_path.exists()
    
    def test_export_unsupported_format(self, tmp_path, source_video):
        """Test exporting with unsupported format."""
        exporter = VideoExporter(output_dir=str(tmp_path))
        
        with pytest.raises(ValueError, match="Unsupported format"):
            exporter.export(source_video, format_ext="xyz")
    
    def test_export_nonexistent_source(self, tmp_path):
        """Test exporting from non-existent source."""
        exporter = VideoExporter(output_dir=str(tmp_path))
        
        with pytest.raises(FileNotFoundError):
            exporter.export("/nonexistent/video.mp4")
    
    def test_verify_export(self, tmp_path, source_video):
        """Test verifying an export."""
        exporter = VideoExporter(output_dir=str(tmp_path))
        
        result = exporter.export(source_video, filename="verify_test")
        verified = exporter.verify_export(result)
        
        assert verified is True
    
    def test_export_multiple_formats(self, tmp_path, source_video):
        """Test exporting in multiple formats."""
        exporter = VideoExporter(output_dir=str(tmp_path))
        
        results = exporter.export_multiple_formats(
            source_video,
            formats=["mp4", "webm"],
            filename="multi_format"
        )
        
        assert len(results) == 2
        assert all(r.success for r in results)
    
    def test_get_export_history(self, tmp_path, source_video):
        """Test getting export history."""
        exporter = VideoExporter(output_dir=str(tmp_path))
        
        exporter.export(source_video, filename="export1")
        exporter.export(source_video, filename="export2")
        
        history = exporter.get_export_history()
        
        assert len(history) == 2
    
    def test_save_to_custom_path(self, tmp_path, source_video):
        """Test saving to custom path."""
        exporter = VideoExporter(output_dir=str(tmp_path / "default"))
        
        custom_path = str(tmp_path / "custom" / "my_video.mp4")
        result = exporter.save_to_custom_path(source_video, custom_path)
        
        assert result.success is True
        assert Path(custom_path).exists()
