"""Integration tests for the complete music video pipeline."""

import pytest
import tempfile
from pathlib import Path

from pipeline.main import MusicVideoPipeline
from pipeline.input_handler import PipelineInput


class TestMusicVideoPipeline:
    """Tests for the complete MusicVideoPipeline."""
    
    @pytest.fixture
    def pipeline(self, tmp_path):
        """Create a pipeline instance with temp output dir."""
        return MusicVideoPipeline(
            target_duration=30.0,
            fps=30,
            resolution=(1920, 1080),
            output_dir=str(tmp_path)
        )
    
    @pytest.fixture
    def minimal_input(self):
        """Create minimal valid input."""
        return PipelineInput(song_prompt="A happy upbeat pop song")
    
    @pytest.fixture
    def full_input(self, tmp_path):
        """Create full input with test images."""
        # Create test image files
        char1 = tmp_path / "char1.jpg"
        char2 = tmp_path / "char2.jpg"
        bg1 = tmp_path / "bg1.jpg"
        elem1 = tmp_path / "elem1.jpg"
        
        for img in [char1, char2, bg1, elem1]:
            img.write_bytes(b"\xff\xd8\xff\xe0")  # Minimal JPEG header
        
        return PipelineInput(
            song_prompt="An emotional love song with beautiful melodies",
            character_images=[str(char1), str(char2)],
            background_images=[str(bg1)],
            element_images=[str(elem1)],
            lyrics="I love you more than words can say\nYou are my everything"
        )
    
    def test_run_minimal_pipeline(self, pipeline, minimal_input):
        """Pipeline should complete with minimal input."""
        result = pipeline.run(minimal_input, validate_images=False)
        
        assert result["success"] is True
        assert result["output_path"] is not None
        assert Path(result["output_path"]).exists()
    
    def test_run_full_pipeline(self, pipeline, full_input):
        """Pipeline should complete with full input."""
        result = pipeline.run(full_input, validate_images=True)
        
        assert result["success"] is True
        assert result["output_path"] is not None
        assert Path(result["output_path"]).exists()
        assert result["stages"]["validation"] == "passed"
        assert result["stages"]["orchestration"] == "completed"
        assert result["stages"]["generation"] == "completed"
        assert result["stages"]["export"] == "completed"
    
    def test_pipeline_stages_executed_in_order(self, pipeline, minimal_input):
        """All pipeline stages should be executed."""
        result = pipeline.run(minimal_input, validate_images=False)
        
        assert "validation" in result["stages"]
        assert "orchestration" in result["stages"]
        assert "generation" in result["stages"]
        assert "export" in result["stages"]
    
    def test_pipeline_output_is_mp4(self, pipeline, minimal_input):
        """Output file should be MP4."""
        result = pipeline.run(minimal_input, validate_images=False)
        
        assert result["output_path"].endswith(".mp4")
    
    def test_pipeline_custom_output_filename(self, pipeline, minimal_input):
        """Pipeline should use custom output filename."""
        result = pipeline.run(
            minimal_input,
            output_filename="my_music_video.mp4",
            validate_images=False
        )
        
        assert "my_music_video.mp4" in result["output_path"]
    
    def test_pipeline_with_invalid_images_fails(self, pipeline):
        """Pipeline should fail with invalid image paths."""
        input_data = PipelineInput(
            song_prompt="Test song",
            character_images=["/nonexistent/image.jpg"]
        )
        
        result = pipeline.run(input_data, validate_images=True)
        
        assert result["success"] is False
        assert "Invalid image paths" in result["error"]
    
    def test_pipeline_orchestration_details(self, pipeline, minimal_input):
        """Pipeline should include orchestration details."""
        result = pipeline.run(minimal_input, validate_images=False)
        
        assert "orchestration_details" in result
        assert result["orchestration_details"]["scenes_count"] > 0
        assert result["orchestration_details"]["total_duration"] > 0
    
    def test_pipeline_generation_details(self, pipeline, minimal_input):
        """Pipeline should include generation details."""
        result = pipeline.run(minimal_input, validate_images=False)
        
        assert "generation_details" in result
        assert result["generation_details"]["total_frames"] > 0
        assert result["generation_details"]["fps"] == 30
    
    def test_pipeline_export_details(self, pipeline, minimal_input):
        """Pipeline should include export details."""
        result = pipeline.run(minimal_input, validate_images=False)
        
        assert "export_details" in result
        assert result["export_details"]["file_size_bytes"] > 0
        assert result["export_details"]["duration_seconds"] > 0
    
    def test_run_from_dict(self, pipeline):
        """Pipeline should run from dictionary input."""
        input_dict = {
            "song_prompt": "A rock anthem about freedom",
            "character_images": [],
            "background_images": [],
            "element_images": [],
            "lyrics": "Freedom is calling"
        }
        
        result = pipeline.run_from_dict(input_dict)
        
        assert result["success"] is True
        assert result["output_path"] is not None


class TestPipelineConfiguration:
    """Tests for pipeline configuration options."""
    
    def test_custom_duration(self, tmp_path):
        """Pipeline should respect custom duration."""
        pipeline = MusicVideoPipeline(
            target_duration=120.0,
            output_dir=str(tmp_path)
        )
        
        input_data = PipelineInput(song_prompt="Long song")
        result = pipeline.run(input_data, validate_images=False)
        
        # Longer duration should produce more content
        assert result["orchestration_details"]["total_duration"] >= 60.0
    
    def test_custom_resolution(self, tmp_path):
        """Pipeline should respect custom resolution."""
        pipeline = MusicVideoPipeline(
            resolution=(3840, 2160),
            output_dir=str(tmp_path)
        )
        
        input_data = PipelineInput(song_prompt="4K video")
        result = pipeline.run(input_data, validate_images=False)
        
        assert result["generation_details"]["resolution"] == "3840x2160"
    
    def test_custom_fps(self, tmp_path):
        """Pipeline should respect custom fps."""
        pipeline = MusicVideoPipeline(
            fps=60,
            output_dir=str(tmp_path)
        )
        
        input_data = PipelineInput(song_prompt="High fps video")
        result = pipeline.run(input_data, validate_images=False)
        
        assert result["generation_details"]["fps"] == 60
