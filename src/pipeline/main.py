"""Main entry point for the Music Video Generation Pipeline.

🚀 NEXT-GEN MULTIMODEL MUSIC VIDEO PIPELINE 🚀

Revolutionary features:
- Multi-model backend support (local/cloud/hybrid)
- Ultra-low compute mode with CHEAT CODES
- Intelligent caching & scene fingerprinting
- Frame interpolation for 2-4x speed boost
- Streaming pipeline (constant memory)
"""

import argparse
import json
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Optional
import sys

from .input_handler import PipelineInput, create_input_from_dict
from .orchestrator import AIOrchestrator, OrchestrationResult, ComputeMode, ModelBackend
from .video_generator import VideoGenerator, VideoGenerationResult, RenderQuality
from .exporter import VideoExporter, ExportResult


# Default output directory using platform-agnostic temp path
DEFAULT_OUTPUT_DIR = str(Path(tempfile.gettempdir()) / "music_video_output")


class MusicVideoPipeline:
    """Main pipeline for end-to-end music video generation.
    
    🚀 NEXT-GEN MULTIMODEL PIPELINE with CHEAT CODES 🚀
    
    Revolutionary optimizations:
    - CHEAT CODE #1: Scene fingerprinting & caching
    - CHEAT CODE #2: Lazy evaluation pipeline
    - CHEAT CODE #3: Smart analysis caching
    - CHEAT CODE #4: Streaming frame generation
    - CHEAT CODE #5: Frame interpolation (2-4x speed)
    - CHEAT CODE #6: Quality presets for instant tradeoffs
    - CHEAT CODE #7: Multi-model backend selection
    """
    
    def __init__(
        self,
        target_duration: float = 60.0,
        fps: int = 30,
        resolution: tuple[int, int] = (1920, 1080),
        output_dir: Optional[str] = None,
        compute_mode: ComputeMode = ComputeMode.BALANCED,
        model_backend: ModelBackend = ModelBackend.LOCAL_FAST,
        render_quality: RenderQuality = RenderQuality.STANDARD
    ) -> None:
        """Initialize the music video pipeline with next-gen options.
        
        Args:
            target_duration: Target video duration in seconds.
            fps: Frames per second for output.
            resolution: Output video resolution (width, height).
            output_dir: Directory for output files.
            compute_mode: Optimization mode (CHEAT CODES!).
            model_backend: AI model backend for multimodel support.
            render_quality: Render quality preset.
        """
        self.target_duration = target_duration
        self.fps = fps
        self.resolution = resolution
        self.output_dir = output_dir or DEFAULT_OUTPUT_DIR
        self.compute_mode = compute_mode
        self.model_backend = model_backend
        self.render_quality = render_quality
        
        # Initialize pipeline components with next-gen options
        self.orchestrator = AIOrchestrator(
            target_duration=target_duration,
            compute_mode=compute_mode,
            model_backend=model_backend
        )
        self.generator = VideoGenerator(
            fps=fps,
            resolution=resolution,
            output_dir=self.output_dir,
            quality=render_quality,
            enable_frame_interpolation=compute_mode in [ComputeMode.ULTRA_LOW, ComputeMode.TURBO]
        )
        self.exporter = VideoExporter(output_dir=self.output_dir)
    
    def run(
        self,
        pipeline_input: PipelineInput,
        output_filename: str = "music_video.mp4",
        validate_images: bool = True
    ) -> dict:
        """Run the complete music video generation pipeline.
        
        Args:
            pipeline_input: All user inputs for the video.
            output_filename: Name for the output MP4 file.
            validate_images: Whether to validate image paths exist.
            
        Returns:
            Dictionary containing pipeline results and status.
        """
        result = {
            "success": False,
            "stages": {},
            "output_path": None,
            "error": None
        }
        
        try:
            # Stage 1: Validate inputs
            if validate_images:
                invalid_images = pipeline_input.validate_all_images()
                if invalid_images:
                    result["error"] = f"Invalid image paths: {invalid_images}"
                    result["stages"]["validation"] = "failed"
                    return result
            
            result["stages"]["validation"] = "passed"
            
            # Stage 2: AI Orchestration
            orchestration_result = self.orchestrator.orchestrate(pipeline_input)
            result["stages"]["orchestration"] = orchestration_result.status.value
            
            if not orchestration_result.is_successful():
                result["error"] = orchestration_result.error_message or "Orchestration failed"
                return result
            
            result["orchestration_details"] = {
                "scenes_count": len(orchestration_result.scenes),
                "total_duration": orchestration_result.total_duration_seconds,
                "song_analysis": orchestration_result.song_analysis
            }
            
            # Stage 3: Video Generation
            generation_result = self.generator.generate(orchestration_result)
            result["stages"]["generation"] = generation_result.status.value
            
            if not generation_result.is_successful():
                result["error"] = generation_result.error_message or "Video generation failed"
                return result
            
            result["generation_details"] = {
                "total_frames": generation_result.total_frames,
                "resolution": f"{generation_result.resolution[0]}x{generation_result.resolution[1]}",
                "fps": generation_result.fps
            }
            
            # Stage 4: Export to MP4
            export_result = self.exporter.export(generation_result, output_filename)
            result["stages"]["export"] = export_result.status.value
            
            if not export_result.is_successful():
                result["error"] = export_result.error_message or "Export failed"
                return result
            
            result["success"] = True
            result["output_path"] = export_result.output_path
            result["export_details"] = {
                "file_size_bytes": export_result.file_size_bytes,
                "duration_seconds": export_result.duration_seconds
            }
            
            return result
            
        except Exception as e:
            result["error"] = str(e)
            return result
    
    def run_from_dict(
        self,
        input_data: dict,
        output_filename: str = "music_video.mp4"
    ) -> dict:
        """Run pipeline from a dictionary of input data.
        
        Args:
            input_data: Dictionary containing all input parameters.
            output_filename: Name for the output MP4 file.
            
        Returns:
            Dictionary containing pipeline results and status.
        """
        pipeline_input = create_input_from_dict(input_data)
        return self.run(pipeline_input, output_filename, validate_images=False)


def main() -> None:
    """Main CLI entry point for the music video pipeline."""
    parser = argparse.ArgumentParser(
        description="End-to-end AI Music Video Generation Pipeline"
    )
    
    parser.add_argument(
        "--song-prompt",
        required=True,
        help="Text description or prompt for the song/music"
    )
    
    parser.add_argument(
        "--character-images",
        nargs="*",
        default=[],
        help="Paths to character reference images (up to 5)"
    )
    
    parser.add_argument(
        "--additional-character",
        help="Path to an additional character image"
    )
    
    parser.add_argument(
        "--background-images",
        nargs="*",
        default=[],
        help="Paths to background reference images (up to 5)"
    )
    
    parser.add_argument(
        "--element-images",
        nargs="*",
        default=[],
        help="Paths to element/prop images for video (up to 5)"
    )
    
    parser.add_argument(
        "--lyrics",
        help="Lyrics text for improved lip syncing"
    )
    
    parser.add_argument(
        "--lyrics-file",
        help="Path to a file containing lyrics"
    )
    
    parser.add_argument(
        "--output",
        default="music_video.mp4",
        help="Output filename for the MP4 video"
    )
    
    parser.add_argument(
        "--output-dir",
        help="Output directory for the video"
    )
    
    parser.add_argument(
        "--duration",
        type=float,
        default=60.0,
        help="Target video duration in seconds"
    )
    
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Frames per second for output"
    )
    
    parser.add_argument(
        "--resolution",
        default="1920x1080",
        help="Output resolution (e.g., 1920x1080)"
    )
    
    parser.add_argument(
        "--json-input",
        help="Path to JSON file containing all input parameters"
    )
    
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validation of image paths"
    )
    
    # 🚀 NEXT-GEN OPTIONS - CHEAT CODES! 🎮
    parser.add_argument(
        "--compute-mode",
        choices=["ultra_low", "balanced", "quality", "turbo"],
        default="balanced",
        help="🎮 CHEAT CODE: Compute optimization mode (ultra_low=max caching, turbo=parallel)"
    )
    
    parser.add_argument(
        "--model-backend",
        choices=["local_fast", "local_quality", "cloud_api", "hybrid"],
        default="local_fast",
        help="🚀 Multimodel backend selection for AI processing"
    )
    
    parser.add_argument(
        "--render-quality",
        choices=["preview", "draft", "standard", "high"],
        default="standard",
        help="🎮 CHEAT CODE: Render quality preset (preview=360p fast, high=4K slow)"
    )
    
    args = parser.parse_args()
    
    # Parse next-gen options
    compute_mode_map = {
        "ultra_low": ComputeMode.ULTRA_LOW,
        "balanced": ComputeMode.BALANCED,
        "quality": ComputeMode.QUALITY,
        "turbo": ComputeMode.TURBO
    }
    compute_mode = compute_mode_map[args.compute_mode]
    
    model_backend_map = {
        "local_fast": ModelBackend.LOCAL_FAST,
        "local_quality": ModelBackend.LOCAL_QUALITY,
        "cloud_api": ModelBackend.CLOUD_API,
        "hybrid": ModelBackend.HYBRID
    }
    model_backend = model_backend_map[args.model_backend]
    
    render_quality_map = {
        "preview": RenderQuality.PREVIEW,
        "draft": RenderQuality.DRAFT,
        "standard": RenderQuality.STANDARD,
        "high": RenderQuality.HIGH
    }
    render_quality = render_quality_map[args.render_quality]
    
    # Parse resolution
    try:
        width, height = args.resolution.split("x")
        resolution = (int(width), int(height))
    except ValueError:
        print(f"Error: Invalid resolution format '{args.resolution}'. Use WIDTHxHEIGHT.")
        sys.exit(1)
    
    # Handle JSON input
    if args.json_input:
        try:
            with open(args.json_input, "r") as f:
                input_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading JSON input: {e}")
            sys.exit(1)
    else:
        # Read lyrics from file if provided
        lyrics = args.lyrics
        if args.lyrics_file:
            try:
                with open(args.lyrics_file, "r") as f:
                    lyrics = f.read()
            except FileNotFoundError:
                print(f"Error: Lyrics file not found: {args.lyrics_file}")
                sys.exit(1)
        
        input_data = {
            "song_prompt": args.song_prompt,
            "character_images": args.character_images,
            "additional_character_image": args.additional_character,
            "background_images": args.background_images,
            "element_images": args.element_images,
            "lyrics": lyrics
        }
    
    # Initialize and run pipeline with NEXT-GEN options
    pipeline = MusicVideoPipeline(
        target_duration=args.duration,
        fps=args.fps,
        resolution=resolution,
        output_dir=args.output_dir,
        compute_mode=compute_mode,
        model_backend=model_backend,
        render_quality=render_quality
    )
    
    try:
        pipeline_input = create_input_from_dict(input_data)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print("🚀 NEXT-GEN Music Video Generation Pipeline 🚀")
    print("=" * 50)
    print(f"Song prompt: {pipeline_input.song_prompt[:50]}...")
    print(f"Character images: {len(pipeline_input.character_images)}")
    print(f"Background images: {len(pipeline_input.background_images)}")
    print(f"Element images: {len(pipeline_input.element_images)}")
    print(f"Has lyrics: {pipeline_input.has_lyrics()}")
    print()
    print("🎮 CHEAT CODES ACTIVE:")
    print(f"  Compute Mode: {compute_mode.value}")
    print(f"  Model Backend: {model_backend.value}")
    print(f"  Render Quality: {render_quality.value}")
    print()
    
    result = pipeline.run(
        pipeline_input,
        output_filename=args.output,
        validate_images=not args.skip_validation
    )
    
    if result["success"]:
        print("✅ Pipeline completed successfully!")
        print(f"Output: {result['output_path']}")
        print(f"Duration: {result['export_details']['duration_seconds']}s")
        print(f"File size: {result['export_details']['file_size_bytes']} bytes")
    else:
        print(f"❌ Pipeline failed: {result['error']}")
        print(f"Stages: {result['stages']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
