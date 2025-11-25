"""AI Orchestration module for music video generation.

This module handles the AI orchestration of all inputs to generate
music video content, integrating song prompts, images, and lyrics.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from pathlib import Path

from .input_handler import PipelineInput


class OrchestrationStatus(Enum):
    """Status of the orchestration process."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SceneDescription:
    """Description of a single scene in the music video.
    
    Attributes:
        scene_id: Unique identifier for the scene.
        description: Text description of the scene content.
        duration_seconds: Duration of the scene in seconds.
        character_references: List of character image paths used.
        background_reference: Background image path if applicable.
        element_references: List of element image paths used.
        has_lip_sync: Whether lip syncing is applied.
    """
    scene_id: int
    description: str
    duration_seconds: float
    character_references: list[str] = field(default_factory=list)
    background_reference: Optional[str] = None
    element_references: list[str] = field(default_factory=list)
    has_lip_sync: bool = False


@dataclass 
class OrchestrationResult:
    """Result from the AI orchestration process.
    
    Attributes:
        status: Current status of orchestration.
        scenes: List of generated scene descriptions.
        total_duration_seconds: Total duration of the music video.
        song_analysis: Analysis of the song prompt.
        error_message: Error message if orchestration failed.
    """
    status: OrchestrationStatus
    scenes: list[SceneDescription] = field(default_factory=list)
    total_duration_seconds: float = 0.0
    song_analysis: Optional[str] = None
    error_message: Optional[str] = None
    
    def is_successful(self) -> bool:
        """Check if orchestration completed successfully.
        
        Returns:
            True if status is COMPLETED and scenes were generated.
        """
        return self.status == OrchestrationStatus.COMPLETED and len(self.scenes) > 0


class AIOrchestrator:
    """AI Orchestrator for music video generation.
    
    This class coordinates all AI components to transform user inputs
    into a structured plan for video generation.
    """
    
    DEFAULT_SCENE_DURATION = 5.0  # seconds
    MIN_SCENES = 4
    MAX_SCENES = 20
    
    def __init__(self, target_duration: float = 60.0) -> None:
        """Initialize the orchestrator.
        
        Args:
            target_duration: Target duration for the music video in seconds.
        """
        self.target_duration = target_duration
    
    def orchestrate(self, pipeline_input: PipelineInput) -> OrchestrationResult:
        """Orchestrate all inputs to generate music video plan.
        
        This method analyzes the song prompt, processes all images,
        and creates a structured scene-by-scene plan for the video.
        
        Args:
            pipeline_input: All user inputs for the video.
            
        Returns:
            OrchestrationResult containing scene descriptions and metadata.
        """
        try:
            # Analyze the song prompt
            song_analysis = self._analyze_song_prompt(pipeline_input.song_prompt)
            
            # Calculate number of scenes based on target duration
            num_scenes = self._calculate_scene_count()
            
            # Generate scene descriptions
            scenes = self._generate_scenes(
                num_scenes=num_scenes,
                pipeline_input=pipeline_input,
                song_analysis=song_analysis
            )
            
            # Calculate total duration
            total_duration = sum(scene.duration_seconds for scene in scenes)
            
            return OrchestrationResult(
                status=OrchestrationStatus.COMPLETED,
                scenes=scenes,
                total_duration_seconds=total_duration,
                song_analysis=song_analysis
            )
            
        except Exception as e:
            return OrchestrationResult(
                status=OrchestrationStatus.FAILED,
                error_message=str(e)
            )
    
    def _analyze_song_prompt(self, song_prompt: str) -> str:
        """Analyze the song prompt to extract themes and mood.
        
        Args:
            song_prompt: The user's song description.
            
        Returns:
            Analysis summary of the song.
        """
        # Extract key themes from the prompt
        prompt_lower = song_prompt.lower()
        
        themes = []
        if any(word in prompt_lower for word in ["happy", "joy", "upbeat", "fun"]):
            themes.append("upbeat/joyful")
        if any(word in prompt_lower for word in ["sad", "melancholy", "emotional"]):
            themes.append("emotional/melancholic")
        if any(word in prompt_lower for word in ["rock", "energy", "power"]):
            themes.append("energetic/powerful")
        if any(word in prompt_lower for word in ["love", "romance", "heart"]):
            themes.append("romantic")
        if any(word in prompt_lower for word in ["dance", "electronic", "beat"]):
            themes.append("dance/electronic")
        
        if not themes:
            themes.append("general/artistic")
        
        return f"Song analysis: {', '.join(themes)}. Based on prompt: {song_prompt[:100]}"
    
    def _calculate_scene_count(self) -> int:
        """Calculate the number of scenes based on target duration.
        
        Returns:
            Number of scenes to generate.
        """
        calculated = int(self.target_duration / self.DEFAULT_SCENE_DURATION)
        return max(self.MIN_SCENES, min(calculated, self.MAX_SCENES))
    
    def _generate_scenes(
        self,
        num_scenes: int,
        pipeline_input: PipelineInput,
        song_analysis: str
    ) -> list[SceneDescription]:
        """Generate scene descriptions for the music video.
        
        Args:
            num_scenes: Number of scenes to generate.
            pipeline_input: All user inputs.
            song_analysis: Analysis of the song prompt.
            
        Returns:
            List of scene descriptions.
        """
        scenes = []
        has_lyrics = pipeline_input.has_lyrics()
        
        # Distribute images across scenes
        char_images = pipeline_input.character_images.copy()
        if pipeline_input.additional_character_image:
            char_images.append(pipeline_input.additional_character_image)
        
        bg_images = pipeline_input.background_images.copy()
        element_images = pipeline_input.element_images.copy()
        
        scene_types = [
            "Opening/Intro",
            "Character Introduction", 
            "Main Verse",
            "Chorus",
            "Bridge",
            "Climax",
            "Resolution",
            "Closing/Outro"
        ]
        
        for i in range(num_scenes):
            scene_type = scene_types[i % len(scene_types)]
            
            # Assign images to scenes in rotation
            scene_chars = []
            if char_images:
                scene_chars = [char_images[i % len(char_images)]]
            
            scene_bg = None
            if bg_images:
                scene_bg = bg_images[i % len(bg_images)]
            
            scene_elements = []
            if element_images:
                scene_elements = [element_images[i % len(element_images)]]
            
            scene = SceneDescription(
                scene_id=i + 1,
                description=f"{scene_type} scene for '{pipeline_input.song_prompt[:50]}...'",
                duration_seconds=self.DEFAULT_SCENE_DURATION,
                character_references=scene_chars,
                background_reference=scene_bg,
                element_references=scene_elements,
                has_lip_sync=has_lyrics and i % 2 == 0  # Apply lip sync to alternate scenes
            )
            scenes.append(scene)
        
        return scenes
