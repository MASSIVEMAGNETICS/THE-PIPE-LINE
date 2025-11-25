"""Main entry point for the Music Video Generation Pipeline.

This module provides the main pipeline class and CLI interface for
generating music videos from user inputs.
"""

import argparse
import json
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Optional
import sys

from .input_handler import PipelineInput, create_input_from_dict
from .orchestrator import AIOrchestrator, OrchestrationResult
from .video_generator import VideoGenerator, VideoGenerationResult
from .exporter import VideoExporter, ExportResult


# Default output directory using platform-agnostic temp path
DEFAULT_OUTPUT_DIR = str(Path(tempfile.gettempdir()) / "music_video_output")


class MusicVideoPipeline:
    """Main pipeline for end-to-end music video generation.
    
    This class orchestrates all components of the pipeline to transform
    user inputs into a complete music video in MP4 format.
    """
    
    def __init__(
        self,
        target_duration: float = 60.0,
        fps: int = 30,
        resolution: tuple[int, int] = (1920, 1080),
        output_dir: Optional[str] = None
    ) -> None:
        """Initialize the music video pipeline.
        
        Args:
            target_duration: Target video duration in seconds.
            fps: Frames per second for output.
            resolution: Output video resolution (width, height).
            output_dir: Directory for output files.
        """
        self.target_duration = target_duration
        self.fps = fps
        self.resolution = resolution
        self.output_dir = output_dir or DEFAULT_OUTPUT_DIR
        
        # Initialize pipeline components
        self.orchestrator = AIOrchestrator(target_duration=target_duration)
        self.generator = VideoGenerator(
            fps=fps,
            resolution=resolution,
            output_dir=self.output_dir
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
    
    args = parser.parse_args()
    
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
    
    # Initialize and run pipeline
    pipeline = MusicVideoPipeline(
        target_duration=args.duration,
        fps=args.fps,
        resolution=resolution,
        output_dir=args.output_dir
    )
    
    try:
        pipeline_input = create_input_from_dict(input_data)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print("Starting Music Video Generation Pipeline...")
    print(f"Song prompt: {pipeline_input.song_prompt[:50]}...")
    print(f"Character images: {len(pipeline_input.character_images)}")
    print(f"Background images: {len(pipeline_input.background_images)}")
    print(f"Element images: {len(pipeline_input.element_images)}")
    print(f"Has lyrics: {pipeline_input.has_lyrics()}")
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
