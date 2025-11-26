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
