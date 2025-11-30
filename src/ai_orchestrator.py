"""
AI Orchestrator for the music video generation pipeline.

This module coordinates the AI-powered generation of music video components:
- Scene planning based on audio analysis
- Character animation generation
- Background scene generation
- Element integration
- Lip sync coordination (when lyrics are provided)
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .input_handlers import PipelineInputs

logger = logging.getLogger(__name__)


@dataclass
class Scene:
    """Represents a single scene in the music video."""
    
    scene_id: int
    start_time: float
    end_time: float
    description: str
    character_ids: List[int] = field(default_factory=list)
    background_id: Optional[int] = None
    element_ids: List[int] = field(default_factory=list)
    transitions: Dict[str, str] = field(default_factory=dict)
    camera_movement: str = "static"
    mood: str = "neutral"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scene to dictionary."""
        return {
            "scene_id": self.scene_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "description": self.description,
            "character_ids": self.character_ids,
            "background_id": self.background_id,
            "element_ids": self.element_ids,
            "transitions": self.transitions,
            "camera_movement": self.camera_movement,
            "mood": self.mood
        }


@dataclass
class VideoScript:
    """Complete video script with all scenes."""
    
    scenes: List[Scene] = field(default_factory=list)
    total_duration: float = 0.0
    fps: int = 30
    resolution: tuple = (1920, 1080)
    
    def add_scene(self, scene: Scene) -> None:
        """Add a scene to the script."""
        self.scenes.append(scene)
        if scene.end_time > self.total_duration:
            self.total_duration = scene.end_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert script to dictionary."""
        return {
            "scenes": [s.to_dict() for s in self.scenes],
            "total_duration": self.total_duration,
            "fps": self.fps,
            "resolution": list(self.resolution)
        }
    
    def to_json(self) -> str:
        """Convert script to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AIOrchestrator:
    """
    AI Orchestrator that coordinates the entire music video generation process.
    
    This class analyzes inputs and creates a comprehensive video script
    that guides the generation of all video components.
    """
    
    def __init__(self, inputs: PipelineInputs, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI Orchestrator.
        
        Args:
            inputs: PipelineInputs containing all user inputs
            config: Optional configuration dictionary
        """
        self.inputs = inputs
        self.config = config or {}
        self.video_script: Optional[VideoScript] = None
        self._generation_context: Dict[str, Any] = {}
    
    def analyze_audio(self) -> Dict[str, Any]:
        """
        Analyze the audio input to extract features for video generation.
        
        Returns:
            Dictionary containing audio analysis results
        """
        logger.info("Analyzing audio input...")
        
        analysis = {
            "duration": self.inputs.audio.duration_seconds or 180.0,  # Default 3 minutes
            "tempo": 120,  # Default BPM
            "sections": [],
            "beats": [],
            "mood_progression": []
        }
        
        # If we have actual audio file, we would analyze it here
        if self.inputs.audio.file_path:
            logger.info(f"Audio file detected: {self.inputs.audio.file_path}")
            # In production, integrate with audio analysis libraries
            # like librosa or essentia
        
        if self.inputs.audio.prompt_description:
            logger.info(f"Audio prompt: {self.inputs.audio.prompt_description}")
            # Use the prompt to guide generation style
        
        return analysis
    
    def analyze_lyrics(self) -> Dict[str, Any]:
        """
        Analyze lyrics for lip sync and scene timing.
        
        Returns:
            Dictionary containing lyrics analysis
        """
        logger.info("Analyzing lyrics input...")
        
        analysis = {
            "has_lyrics": self.inputs.lyrics.has_lyrics(),
            "word_count": 0,
            "sections": [],
            "lip_sync_data": []
        }
        
        if self.inputs.lyrics.has_lyrics():
            lyrics_text = self.inputs.lyrics.get_lyrics()
            if lyrics_text:
                words = lyrics_text.split()
                analysis["word_count"] = len(words)
            
            if self.inputs.lyrics.timestamps:
                analysis["lip_sync_data"] = self.inputs.lyrics.timestamps
        
        return analysis
    
    def plan_scenes(self, audio_analysis: Dict[str, Any], 
                    lyrics_analysis: Dict[str, Any]) -> VideoScript:
        """
        Plan video scenes based on audio and lyrics analysis.
        
        Args:
            audio_analysis: Results from audio analysis
            lyrics_analysis: Results from lyrics analysis
            
        Returns:
            VideoScript containing all planned scenes
        """
        logger.info("Planning video scenes...")
        
        script = VideoScript()
        duration = audio_analysis.get("duration", 180.0)
        
        # Get available assets
        character_images = self.inputs.characters.get_all_images()
        background_images = self.inputs.backgrounds.get_images()
        element_images = self.inputs.elements.get_images()
        
        # Determine number of scenes based on duration
        # Roughly one scene every 15-30 seconds
        avg_scene_duration = 20.0
        num_scenes = max(1, int(duration / avg_scene_duration))
        
        scene_duration = duration / num_scenes
        
        for i in range(num_scenes):
            start_time = i * scene_duration
            end_time = start_time + scene_duration
            
            # Assign assets cyclically
            char_ids = [i % len(character_images)] if character_images else []
            bg_id = i % len(background_images) if background_images else None
            elem_ids = [i % len(element_images)] if element_images else []
            
            # Determine mood and camera movement
            moods = ["energetic", "calm", "intense", "dreamy", "dramatic"]
            camera_movements = ["static", "pan_left", "pan_right", "zoom_in", "zoom_out", "dolly"]
            
            scene = Scene(
                scene_id=i + 1,
                start_time=start_time,
                end_time=end_time,
                description=f"Scene {i + 1}: Musical segment",
                character_ids=char_ids,
                background_id=bg_id,
                element_ids=elem_ids,
                transitions={"in": "fade", "out": "fade"} if i > 0 else {"in": "none", "out": "fade"},
                camera_movement=camera_movements[i % len(camera_movements)],
                mood=moods[i % len(moods)]
            )
            
            script.add_scene(scene)
        
        logger.info(f"Planned {len(script.scenes)} scenes for {duration}s video")
        return script
    
    def generate_generation_context(self) -> Dict[str, Any]:
        """
        Generate the context needed for AI-powered generation.
        
        Returns:
            Dictionary containing all generation context
        """
        logger.info("Generating AI context...")
        
        context = {
            "inputs_summary": self.inputs.get_summary(),
            "video_script": self.video_script.to_dict() if self.video_script else None,
            "generation_params": {
                "fps": self.config.get("fps", 30),
                "resolution": self.config.get("resolution", (1920, 1080)),
                "quality": self.config.get("quality", "high"),
                "style": self.config.get("style", "cinematic")
            },
            "ai_prompts": self._generate_ai_prompts()
        }
        
        self._generation_context = context
        return context
    
    def _generate_ai_prompts(self) -> List[Dict[str, str]]:
        """Generate AI prompts for each scene."""
        prompts = []
        
        if self.video_script:
            for scene in self.video_script.scenes:
                prompt = {
                    "scene_id": scene.scene_id,
                    "visual_prompt": f"Generate a {scene.mood} scene with {scene.camera_movement} camera movement",
                    "timing": f"{scene.start_time:.2f}s - {scene.end_time:.2f}s"
                }
                prompts.append(prompt)
        
        return prompts
    
    def orchestrate(self) -> Dict[str, Any]:
        """
        Main orchestration method that coordinates the entire generation process.
        
        Returns:
            Dictionary containing the complete generation plan
        """
        logger.info("Starting AI orchestration...")
        
        # Validate inputs
        self.inputs.validate_all()
        
        # Analyze audio
        audio_analysis = self.analyze_audio()
        
        # Analyze lyrics
        lyrics_analysis = self.analyze_lyrics()
        
        # Plan scenes
        self.video_script = self.plan_scenes(audio_analysis, lyrics_analysis)
        
        # Generate context for video generation
        generation_context = self.generate_generation_context()
        
        logger.info("AI orchestration complete")
        
        return {
            "status": "success",
            "audio_analysis": audio_analysis,
            "lyrics_analysis": lyrics_analysis,
            "video_script": self.video_script.to_dict(),
            "generation_context": generation_context
        }
    
    def get_video_script(self) -> Optional[VideoScript]:
        """Get the generated video script."""
        return self.video_script
    
    def export_script(self, filepath: str) -> bool:
        """
        Export the video script to a JSON file.
        
        Args:
            filepath: Path to save the script
            
        Returns:
            True if successful
        """
        if not self.video_script:
            raise ValueError("No video script generated. Run orchestrate() first.")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.video_script.to_json())
        
        logger.info(f"Video script exported to: {filepath}")
        return True
