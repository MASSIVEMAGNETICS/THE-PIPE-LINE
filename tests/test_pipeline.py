"""
Tests for the main pipeline module.
"""

import pytest
from pathlib import Path

from src.pipeline import (
    MusicVideoPipeline,
    PipelineConfig,
    PipelineResult,
    create_pipeline,
    generate_music_video,
)
from src.exporter import ExportMetadata


class TestPipelineConfig:
    """Tests for PipelineConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = PipelineConfig()
        
        assert config.fps == 30
        assert config.resolution == (1920, 1080)
        assert config.quality == "high"
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = PipelineConfig(
            fps=60,
            resolution=(3840, 2160),
            quality="medium"
        )
        
        assert config.fps == 60
        assert config.resolution == (3840, 2160)
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = PipelineConfig(fps=24, style="anime")
        
        result = config.to_dict()
        
        assert result["fps"] == 24
        assert result["style"] == "anime"


class TestMusicVideoPipeline:
    """Tests for MusicVideoPipeline class."""
    
    def test_pipeline_creation(self):
        """Test creating a pipeline."""
        pipeline = MusicVideoPipeline()
        
        assert pipeline.config is not None
        assert pipeline.inputs is not None
    
    def test_add_audio_file(self, tmp_path):
        """Test adding audio file input."""
        audio_file = tmp_path / "song.mp3"
        audio_file.touch()
        
        pipeline = MusicVideoPipeline()
        result = pipeline.add_audio(file_path=str(audio_file))
        
        assert result == pipeline  # Method chaining
        assert pipeline.inputs.audio.file_path == str(audio_file)
    
    def test_add_audio_prompt(self):
        """Test adding audio prompt."""
        pipeline = MusicVideoPipeline()
        pipeline.add_audio(
            prompt_description="energetic rock song",
            duration_seconds=120.0
        )
        
        assert pipeline.inputs.audio.prompt_description == "energetic rock song"
        assert pipeline.inputs.audio.duration_seconds == 120.0
    
    def test_add_character_images(self, tmp_path):
        """Test adding character images."""
        images = []
        for i in range(3):
            img = tmp_path / f"char{i}.png"
            img.touch()
            images.append(str(img))
        
        pipeline = MusicVideoPipeline()
        pipeline.add_character_images(images)
        
        assert len(pipeline.inputs.characters.primary_images.image_paths) == 3
    
    def test_add_character_with_additional(self, tmp_path):
        """Test adding character with additional images."""
        primary = tmp_path / "primary.png"
        primary.touch()
        additional = tmp_path / "additional.png"
        additional.touch()
        
        pipeline = MusicVideoPipeline()
        pipeline.add_character_image(str(primary), is_additional=False)
        pipeline.add_character_image(str(additional), is_additional=True)
        
        assert len(pipeline.inputs.characters.primary_images.image_paths) == 1
        assert len(pipeline.inputs.characters.additional_images.image_paths) == 1
    
    def test_add_background_images(self, tmp_path):
        """Test adding background images."""
        images = []
        for i in range(2):
            img = tmp_path / f"bg{i}.jpg"
            img.touch()
            images.append(str(img))
        
        pipeline = MusicVideoPipeline()
        pipeline.add_background_images(images)
        
        assert len(pipeline.inputs.backgrounds.images.image_paths) == 2
    
    def test_add_element_images(self, tmp_path):
        """Test adding element images."""
        elem = tmp_path / "element.png"
        elem.touch()
        
        pipeline = MusicVideoPipeline()
        pipeline.add_element_image(str(elem))
        
        assert len(pipeline.inputs.elements.images.image_paths) == 1
    
    def test_add_lyrics_text(self):
        """Test adding lyrics as text."""
        pipeline = MusicVideoPipeline()
        pipeline.add_lyrics(text="Hello world, this is my song")
        
        assert pipeline.inputs.lyrics.has_lyrics() is True
    
    def test_add_lyrics_file(self, tmp_path):
        """Test adding lyrics from file."""
        lyrics_file = tmp_path / "lyrics.txt"
        lyrics_file.write_text("Verse 1: Testing\nChorus: More testing")
        
        pipeline = MusicVideoPipeline()
        pipeline.add_lyrics(file_path=str(lyrics_file))
        
        assert pipeline.inputs.lyrics.has_lyrics() is True
    
    def test_method_chaining(self, tmp_path):
        """Test method chaining works."""
        audio = tmp_path / "song.mp3"
        audio.touch()
        char = tmp_path / "char.png"
        char.touch()
        bg = tmp_path / "bg.jpg"
        bg.touch()
        
        pipeline = (
            MusicVideoPipeline()
            .add_audio(file_path=str(audio))
            .add_character_image(str(char))
            .add_background_image(str(bg))
            .add_lyrics(text="Test lyrics")
        )
        
        assert pipeline.inputs.audio.file_path is not None
        assert len(pipeline.inputs.characters.get_all_images()) == 1
        assert len(pipeline.inputs.backgrounds.get_images()) == 1
    
    def test_validate_inputs(self, tmp_path):
        """Test input validation."""
        audio = tmp_path / "song.mp3"
        audio.touch()
        
        pipeline = MusicVideoPipeline()
        pipeline.add_audio(file_path=str(audio))
        
        result = pipeline.validate_inputs()
        
        assert result is True
    
    def test_get_input_summary(self):
        """Test getting input summary."""
        pipeline = MusicVideoPipeline()
        pipeline.add_audio(prompt_description="test", duration_seconds=60)
        
        summary = pipeline.get_input_summary()
        
        assert "audio" in summary
        assert summary["audio"]["prompt"] == "test"
    
    def test_set_config(self):
        """Test setting configuration."""
        pipeline = MusicVideoPipeline()
        pipeline.set_config(fps=60, quality="low")
        
        assert pipeline.config.fps == 60
        assert pipeline.config.quality == "low"
    
    def test_reset(self, tmp_path):
        """Test resetting pipeline."""
        audio = tmp_path / "song.mp3"
        audio.touch()
        
        pipeline = MusicVideoPipeline()
        pipeline.add_audio(file_path=str(audio))
        pipeline.reset()
        
        assert pipeline.inputs.audio.file_path is None
    
    def test_run_pipeline(self, tmp_path):
        """Test running the full pipeline."""
        # Create test audio file
        audio = tmp_path / "song.mp3"
        audio.touch()
        
        output_dir = tmp_path / "output"
        
        config = PipelineConfig(output_dir=str(output_dir))
        pipeline = MusicVideoPipeline(config=config)
        pipeline.add_audio(
            file_path=str(audio),
            duration_seconds=10.0
        )
        
        result = pipeline.run()
        
        assert isinstance(result, PipelineResult)
        assert result.success is True
        assert result.output_path is not None
    
    def test_run_with_metadata(self, tmp_path):
        """Test running pipeline with metadata."""
        audio = tmp_path / "song.mp3"
        audio.touch()
        
        output_dir = tmp_path / "output"
        config = PipelineConfig(output_dir=str(output_dir))
        pipeline = MusicVideoPipeline(config=config)
        pipeline.add_audio(file_path=str(audio), duration_seconds=5.0)
        
        metadata = ExportMetadata(title="Test Video", artist="Test Artist")
        result = pipeline.run(metadata=metadata)
        
        assert result.success is True


class TestCreatePipeline:
    """Tests for create_pipeline factory function."""
    
    def test_create_default_pipeline(self):
        """Test creating pipeline with defaults."""
        pipeline = create_pipeline()
        
        assert isinstance(pipeline, MusicVideoPipeline)
    
    def test_create_configured_pipeline(self):
        """Test creating pipeline with config."""
        config = {
            "fps": 60,
            "resolution": [1280, 720],
            "quality": "medium"
        }
        
        pipeline = create_pipeline(config)
        
        assert pipeline.config.fps == 60
        assert pipeline.config.resolution == (1280, 720)


class TestGenerateMusicVideo:
    """Tests for generate_music_video convenience function."""
    
    def test_generate_with_audio_prompt(self, tmp_path):
        """Test generating with audio prompt."""
        result = generate_music_video(
            audio_prompt="test song",
            output_path=str(tmp_path / "output")
        )
        
        assert isinstance(result, PipelineResult)
    
    def test_generate_with_all_inputs(self, tmp_path):
        """Test generating with all input types."""
        # Create test files
        audio = tmp_path / "song.mp3"
        audio.touch()
        char = tmp_path / "char.png"
        char.touch()
        bg = tmp_path / "bg.jpg"
        bg.touch()
        elem = tmp_path / "elem.png"
        elem.touch()
        
        result = generate_music_video(
            audio_file=str(audio),
            character_images=[str(char)],
            background_images=[str(bg)],
            element_images=[str(elem)],
            lyrics="Test lyrics",
            output_path=str(tmp_path / "output")
        )
        
        assert result.success is True
