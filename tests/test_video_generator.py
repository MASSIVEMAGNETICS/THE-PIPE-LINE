"""
Tests for video generator module.
"""

import pytest
from pathlib import Path

from src.video_generator import VideoGenerator, VideoFrame, GenerationProgress
from src.ai_orchestrator import Scene, VideoScript
from src.input_handlers import AudioInput, PipelineInputs


class TestVideoFrame:
    """Tests for VideoFrame class."""
    
    def test_frame_creation(self):
        """Test creating a video frame."""
        frame = VideoFrame(
            frame_number=100,
            timestamp=3.33,
            scene_id=1
        )
        
        assert frame.frame_number == 100
        assert frame.timestamp == 3.33
    
    def test_frame_to_dict(self):
        """Test converting frame to dictionary."""
        frame = VideoFrame(
            frame_number=0,
            timestamp=0.0,
            scene_id=1,
            image_path="/path/to/frame.png"
        )
        
        result = frame.to_dict()
        
        assert result["frame_number"] == 0
        assert result["image_path"] == "/path/to/frame.png"


class TestGenerationProgress:
    """Tests for GenerationProgress class."""
    
    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        progress = GenerationProgress(
            total_frames=100,
            generated_frames=50
        )
        
        assert progress.percentage == 50.0
    
    def test_progress_percentage_zero_frames(self):
        """Test percentage with zero total frames."""
        progress = GenerationProgress(total_frames=0, generated_frames=0)
        
        assert progress.percentage == 0.0
    
    def test_progress_to_dict(self):
        """Test converting progress to dictionary."""
        progress = GenerationProgress(
            total_frames=100,
            generated_frames=75,
            status="generating"
        )
        
        result = progress.to_dict()
        
        assert result["percentage"] == 75.0
        assert result["status"] == "generating"


class TestVideoGenerator:
    """Tests for VideoGenerator class."""
    
    @pytest.fixture
    def basic_script(self):
        """Create a basic video script for testing."""
        script = VideoScript(fps=30, resolution=(1920, 1080))
        scene = Scene(
            scene_id=1,
            start_time=0.0,
            end_time=10.0,
            description="Test scene"
        )
        script.add_scene(scene)
        return script
    
    @pytest.fixture
    def basic_inputs(self):
        """Create basic pipeline inputs for testing."""
        inputs = PipelineInputs()
        inputs.audio = AudioInput(
            prompt_description="test song",
            duration_seconds=10.0
        )
        return inputs
    
    def test_generator_creation(self, basic_inputs, basic_script, tmp_path):
        """Test creating a video generator."""
        generator = VideoGenerator(
            inputs=basic_inputs,
            video_script=basic_script,
            output_dir=str(tmp_path)
        )
        
        assert generator.fps == 30
        assert generator.resolution == (1920, 1080)
    
    def test_setup(self, basic_inputs, basic_script, tmp_path):
        """Test generator setup."""
        generator = VideoGenerator(
            inputs=basic_inputs,
            video_script=basic_script,
            output_dir=str(tmp_path)
        )
        
        result = generator.setup()
        
        assert result is True
        assert generator.temp_dir is not None
        assert generator.temp_dir.exists()
    
    def test_generate_frame(self, basic_inputs, basic_script, tmp_path):
        """Test generating a single frame."""
        generator = VideoGenerator(
            inputs=basic_inputs,
            video_script=basic_script,
            output_dir=str(tmp_path)
        )
        
        frame = generator.generate_frame(frame_number=0, scene_id=1)
        
        assert isinstance(frame, VideoFrame)
        assert frame.frame_number == 0
        assert frame.scene_id == 1
    
    def test_generate_all_frames(self, basic_inputs, basic_script, tmp_path):
        """Test generating all frames."""
        generator = VideoGenerator(
            inputs=basic_inputs,
            video_script=basic_script,
            output_dir=str(tmp_path)
        )
        generator.setup()
        
        result = generator.generate_all_frames()
        
        assert result is True
        assert len(generator.frames) > 0
    
    def test_full_generation(self, basic_inputs, basic_script, tmp_path):
        """Test full video generation."""
        generator = VideoGenerator(
            inputs=basic_inputs,
            video_script=basic_script,
            output_dir=str(tmp_path)
        )
        
        output_path = generator.generate("test_output.mp4")
        
        assert Path(output_path).exists()
        assert generator.progress.status == "complete"
    
    def test_get_progress(self, basic_inputs, basic_script, tmp_path):
        """Test getting generation progress."""
        generator = VideoGenerator(
            inputs=basic_inputs,
            video_script=basic_script,
            output_dir=str(tmp_path)
        )
        
        progress = generator.get_progress()
        
        assert isinstance(progress, GenerationProgress)
        assert progress.status == "pending"
