"""
Tests for AI orchestrator module.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.ai_orchestrator import AIOrchestrator, Scene, VideoScript
from src.input_handlers import (
    AudioInput,
    PipelineInputs,
)


class TestScene:
    """Tests for Scene class."""
    
    def test_scene_creation(self):
        """Test creating a scene."""
        scene = Scene(
            scene_id=1,
            start_time=0.0,
            end_time=20.0,
            description="Opening scene"
        )
        
        assert scene.scene_id == 1
        assert scene.start_time == 0.0
        assert scene.end_time == 20.0
    
    def test_scene_to_dict(self):
        """Test converting scene to dictionary."""
        scene = Scene(
            scene_id=1,
            start_time=0.0,
            end_time=20.0,
            description="Test scene",
            mood="energetic",
            camera_movement="pan_left"
        )
        
        result = scene.to_dict()
        
        assert result["scene_id"] == 1
        assert result["mood"] == "energetic"
        assert result["camera_movement"] == "pan_left"


class TestVideoScript:
    """Tests for VideoScript class."""
    
    def test_add_scene(self):
        """Test adding scenes to script."""
        script = VideoScript()
        
        scene1 = Scene(scene_id=1, start_time=0.0, end_time=20.0, description="Scene 1")
        scene2 = Scene(scene_id=2, start_time=20.0, end_time=40.0, description="Scene 2")
        
        script.add_scene(scene1)
        script.add_scene(scene2)
        
        assert len(script.scenes) == 2
        assert script.total_duration == 40.0
    
    def test_script_to_json(self):
        """Test converting script to JSON."""
        script = VideoScript(fps=30, resolution=(1920, 1080))
        scene = Scene(scene_id=1, start_time=0.0, end_time=10.0, description="Test")
        script.add_scene(scene)
        
        json_str = script.to_json()
        
        assert '"scene_id": 1' in json_str
        assert '"fps": 30' in json_str


class TestAIOrchestrator:
    """Tests for AIOrchestrator class."""
    
    @pytest.fixture
    def basic_inputs(self):
        """Create basic pipeline inputs for testing."""
        inputs = PipelineInputs()
        inputs.audio = AudioInput(
            prompt_description="upbeat song",
            duration_seconds=60.0
        )
        return inputs
    
    def test_orchestrator_creation(self, basic_inputs):
        """Test creating an orchestrator."""
        orchestrator = AIOrchestrator(inputs=basic_inputs)
        
        assert orchestrator.inputs == basic_inputs
        assert orchestrator.video_script is None
    
    def test_analyze_audio(self, basic_inputs):
        """Test audio analysis."""
        orchestrator = AIOrchestrator(inputs=basic_inputs)
        
        analysis = orchestrator.analyze_audio()
        
        assert "duration" in analysis
        assert analysis["duration"] == 60.0
    
    def test_analyze_lyrics_no_lyrics(self, basic_inputs):
        """Test lyrics analysis with no lyrics."""
        orchestrator = AIOrchestrator(inputs=basic_inputs)
        
        analysis = orchestrator.analyze_lyrics()
        
        assert analysis["has_lyrics"] is False
        assert analysis["word_count"] == 0
    
    def test_plan_scenes(self, basic_inputs):
        """Test scene planning."""
        orchestrator = AIOrchestrator(inputs=basic_inputs)
        
        audio_analysis = {"duration": 60.0}
        lyrics_analysis = {"has_lyrics": False}
        
        script = orchestrator.plan_scenes(audio_analysis, lyrics_analysis)
        
        assert isinstance(script, VideoScript)
        assert len(script.scenes) > 0
    
    def test_orchestrate(self, basic_inputs):
        """Test full orchestration."""
        orchestrator = AIOrchestrator(inputs=basic_inputs)
        
        result = orchestrator.orchestrate()
        
        assert result["status"] == "success"
        assert "audio_analysis" in result
        assert "video_script" in result
        assert orchestrator.video_script is not None
    
    def test_export_script(self, basic_inputs, tmp_path):
        """Test exporting video script."""
        orchestrator = AIOrchestrator(inputs=basic_inputs)
        orchestrator.orchestrate()
        
        output_file = tmp_path / "script.json"
        result = orchestrator.export_script(str(output_file))
        
        assert result is True
        assert output_file.exists()
    
    def test_export_script_without_orchestration(self, basic_inputs, tmp_path):
        """Test exporting script without running orchestration first."""
        orchestrator = AIOrchestrator(inputs=basic_inputs)
        output_file = tmp_path / "script.json"
        
        with pytest.raises(ValueError, match="No video script generated"):
            orchestrator.export_script(str(output_file))
