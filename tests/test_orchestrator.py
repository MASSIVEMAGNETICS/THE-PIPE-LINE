"""Tests for AI orchestration module."""

import pytest

from pipeline.input_handler import PipelineInput
from pipeline.orchestrator import (
    AIOrchestrator,
    OrchestrationResult,
    OrchestrationStatus,
    SceneDescription,
)


class TestSceneDescription:
    """Tests for SceneDescription dataclass."""
    
    def test_create_scene_with_defaults(self):
        """Scene should be creatable with minimal parameters."""
        scene = SceneDescription(
            scene_id=1,
            description="Opening scene",
            duration_seconds=5.0
        )
        
        assert scene.scene_id == 1
        assert scene.description == "Opening scene"
        assert scene.duration_seconds == 5.0
        assert scene.character_references == []
        assert scene.background_reference is None
        assert scene.has_lip_sync is False
    
    def test_create_scene_with_all_fields(self):
        """Scene should be creatable with all parameters."""
        scene = SceneDescription(
            scene_id=2,
            description="Main verse",
            duration_seconds=10.0,
            character_references=["char1.jpg"],
            background_reference="bg.jpg",
            element_references=["prop.jpg"],
            has_lip_sync=True
        )
        
        assert scene.scene_id == 2
        assert len(scene.character_references) == 1
        assert scene.background_reference == "bg.jpg"
        assert scene.has_lip_sync is True


class TestOrchestrationResult:
    """Tests for OrchestrationResult dataclass."""
    
    def test_successful_result(self):
        """Successful result should return is_successful True."""
        scene = SceneDescription(
            scene_id=1,
            description="Test",
            duration_seconds=5.0
        )
        
        result = OrchestrationResult(
            status=OrchestrationStatus.COMPLETED,
            scenes=[scene],
            total_duration_seconds=5.0
        )
        
        assert result.is_successful() is True
    
    def test_failed_result(self):
        """Failed result should return is_successful False."""
        result = OrchestrationResult(
            status=OrchestrationStatus.FAILED,
            error_message="Something went wrong"
        )
        
        assert result.is_successful() is False
    
    def test_empty_scenes_not_successful(self):
        """Result with no scenes should not be successful."""
        result = OrchestrationResult(
            status=OrchestrationStatus.COMPLETED,
            scenes=[]
        )
        
        assert result.is_successful() is False


class TestAIOrchestrator:
    """Tests for AIOrchestrator class."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator instance."""
        return AIOrchestrator(target_duration=60.0)
    
    @pytest.fixture
    def minimal_input(self):
        """Create minimal valid input."""
        return PipelineInput(song_prompt="A happy pop song")
    
    @pytest.fixture
    def full_input(self):
        """Create full input with all fields."""
        return PipelineInput(
            song_prompt="An emotional love ballad with soft melodies",
            character_images=["char1.jpg", "char2.jpg"],
            additional_character_image="extra.jpg",
            background_images=["bg1.jpg", "bg2.jpg"],
            element_images=["prop1.jpg"],
            lyrics="I love you so much\nYou mean the world to me"
        )
    
    def test_orchestrate_minimal_input(self, orchestrator, minimal_input):
        """Should successfully orchestrate minimal input."""
        result = orchestrator.orchestrate(minimal_input)
        
        assert result.status == OrchestrationStatus.COMPLETED
        assert result.is_successful()
        assert len(result.scenes) > 0
        assert result.total_duration_seconds > 0
        assert result.song_analysis is not None
    
    def test_orchestrate_full_input(self, orchestrator, full_input):
        """Should successfully orchestrate full input."""
        result = orchestrator.orchestrate(full_input)
        
        assert result.status == OrchestrationStatus.COMPLETED
        assert result.is_successful()
        assert len(result.scenes) > 0
        
        # Check that images are distributed to scenes
        has_char_ref = any(
            len(scene.character_references) > 0 
            for scene in result.scenes
        )
        has_bg_ref = any(
            scene.background_reference is not None 
            for scene in result.scenes
        )
        
        assert has_char_ref
        assert has_bg_ref
    
    def test_orchestrate_with_lyrics_enables_lip_sync(self, orchestrator, full_input):
        """Scenes should have lip sync when lyrics provided."""
        result = orchestrator.orchestrate(full_input)
        
        # At least some scenes should have lip sync enabled
        has_lip_sync = any(scene.has_lip_sync for scene in result.scenes)
        assert has_lip_sync
    
    def test_orchestrate_without_lyrics_no_lip_sync(self, orchestrator, minimal_input):
        """Scenes should not have lip sync without lyrics."""
        result = orchestrator.orchestrate(minimal_input)
        
        # No scenes should have lip sync
        any_lip_sync = any(scene.has_lip_sync for scene in result.scenes)
        assert not any_lip_sync
    
    def test_scene_count_matches_duration(self):
        """Number of scenes should scale with target duration."""
        short_orchestrator = AIOrchestrator(target_duration=20.0)
        long_orchestrator = AIOrchestrator(target_duration=120.0)
        
        input_data = PipelineInput(song_prompt="Test song")
        
        short_result = short_orchestrator.orchestrate(input_data)
        long_result = long_orchestrator.orchestrate(input_data)
        
        # Longer duration should have more scenes
        assert len(long_result.scenes) >= len(short_result.scenes)
    
    def test_song_analysis_detects_themes(self, orchestrator):
        """Song analysis should detect themes from prompt."""
        happy_input = PipelineInput(song_prompt="A happy upbeat dance song")
        result = orchestrator.orchestrate(happy_input)
        
        assert "upbeat" in result.song_analysis.lower() or "dance" in result.song_analysis.lower()
    
    def test_total_duration_matches_scenes(self, orchestrator, minimal_input):
        """Total duration should match sum of scene durations."""
        result = orchestrator.orchestrate(minimal_input)
        
        scene_duration_sum = sum(scene.duration_seconds for scene in result.scenes)
        assert result.total_duration_seconds == scene_duration_sum
