"""Tests for video generation module."""

import pytest
import tempfile
from pathlib import Path

from pipeline.orchestrator import (
    OrchestrationResult,
    OrchestrationStatus,
    SceneDescription,
)
from pipeline.video_generator import (
    VideoGenerator,
    VideoGenerationResult,
    RenderStatus,
    RenderedScene,
)


class TestRenderedScene:
    """Tests for RenderedScene dataclass."""
    
    def test_create_rendered_scene(self):
        """Should create rendered scene with all fields."""
        scene = RenderedScene(
            scene_id=1,
            frame_count=150,
            duration_seconds=5.0,
            temp_path="/tmp/scene_1"
        )
        
        assert scene.scene_id == 1
        assert scene.frame_count == 150
        assert scene.duration_seconds == 5.0
        assert scene.temp_path == "/tmp/scene_1"


class TestVideoGenerationResult:
    """Tests for VideoGenerationResult dataclass."""
    
    def test_successful_result(self):
        """Successful result should return is_successful True."""
        scene = RenderedScene(scene_id=1, frame_count=150, duration_seconds=5.0)
        
        result = VideoGenerationResult(
            status=RenderStatus.COMPLETED,
            rendered_scenes=[scene],
            total_frames=150
        )
        
        assert result.is_successful() is True
    
    def test_failed_result(self):
        """Failed result should return is_successful False."""
        result = VideoGenerationResult(
            status=RenderStatus.FAILED,
            error_message="Render failed"
        )
        
        assert result.is_successful() is False
    
    def test_default_resolution_and_fps(self):
        """Result should have default resolution and fps."""
        result = VideoGenerationResult(status=RenderStatus.PENDING)
        
        assert result.resolution == (1920, 1080)
        assert result.fps == 30
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
    def generator(self, tmp_path):
        """Create a generator instance with temp output dir."""
        return VideoGenerator(
            fps=30,
            resolution=(1920, 1080),
            output_dir=str(tmp_path)
        )
    
    @pytest.fixture
    def successful_orchestration(self):
        """Create a successful orchestration result."""
        scenes = [
            SceneDescription(
                scene_id=1,
                description="Opening scene",
                duration_seconds=5.0,
                character_references=["char.jpg"],
                background_reference="bg.jpg"
            ),
            SceneDescription(
                scene_id=2,
                description="Main verse",
                duration_seconds=5.0,
                has_lip_sync=True
            ),
        ]
        
        return OrchestrationResult(
            status=OrchestrationStatus.COMPLETED,
            scenes=scenes,
            total_duration_seconds=10.0,
            song_analysis="Test analysis"
        )
    
    @pytest.fixture
    def failed_orchestration(self):
        """Create a failed orchestration result."""
        return OrchestrationResult(
            status=OrchestrationStatus.FAILED,
            error_message="Orchestration failed"
        )
    
    def test_generate_from_successful_orchestration(self, generator, successful_orchestration):
        """Should generate video from successful orchestration."""
        result = generator.generate(successful_orchestration)
        
        assert result.status == RenderStatus.COMPLETED
        assert result.is_successful()
        assert len(result.rendered_scenes) == 2
        assert result.total_frames > 0
    
    def test_generate_from_failed_orchestration(self, generator, failed_orchestration):
        """Should fail when orchestration failed."""
        result = generator.generate(failed_orchestration)
        
        assert result.status == RenderStatus.FAILED
        assert not result.is_successful()
        assert "failed orchestration" in result.error_message.lower()
    
    def test_frame_count_calculation(self, generator, successful_orchestration):
        """Frame count should match fps * duration."""
        result = generator.generate(successful_orchestration)
        
        expected_frames = sum(
            int(scene.duration_seconds * generator.fps)
            for scene in successful_orchestration.scenes
        )
        
        assert result.total_frames == expected_frames
    
    def test_scene_metadata_created(self, generator, successful_orchestration, tmp_path):
        """Scene metadata files should be created."""
        result = generator.generate(successful_orchestration)
        
        for rendered_scene in result.rendered_scenes:
            metadata_path = Path(rendered_scene.temp_path) / "metadata.txt"
            assert metadata_path.exists()
    
    def test_resolution_preserved(self, successful_orchestration, tmp_path):
        """Custom resolution should be preserved in result."""
        custom_res = (3840, 2160)
        generator = VideoGenerator(
            resolution=custom_res,
            output_dir=str(tmp_path)
        )
        
        result = generator.generate(successful_orchestration)
        assert result.resolution == custom_res
    
    def test_fps_preserved(self, successful_orchestration, tmp_path):
        """Custom fps should be preserved in result."""
        generator = VideoGenerator(
            fps=60,
            output_dir=str(tmp_path)
        )
        
        result = generator.generate(successful_orchestration)
        assert result.fps == 60
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
