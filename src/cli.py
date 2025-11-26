#!/usr/bin/env python3
"""
Command-line interface for THE-PIPE-LINE music video generation.

Usage:
    python -m src.cli --audio song.mp3 --characters char1.png char2.png --output video.mp4
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

from .pipeline import MusicVideoPipeline, PipelineConfig, generate_music_video
from .exporter import ExportMetadata

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="THE-PIPE-LINE: End-to-End Music Video Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate video with audio and character images
  python -m src.cli --audio song.mp3 --characters char1.png char2.png

  # Full generation with all inputs
  python -m src.cli --audio song.mp3 \\
      --characters char1.png char2.png \\
      --backgrounds bg1.jpg bg2.jpg \\
      --elements prop1.png prop2.png \\
      --lyrics lyrics.txt \\
      --output my_video.mp4

  # Using audio prompt instead of file
  python -m src.cli --audio-prompt "upbeat pop song" --duration 180 \\
      --characters performer.png
        """
    )
    
    # Audio input
    audio_group = parser.add_mutually_exclusive_group(required=True)
    audio_group.add_argument(
        "--audio", "-a",
        type=str,
        help="Path to audio file (mp3, wav, flac, etc.)"
    )
    audio_group.add_argument(
        "--audio-prompt",
        type=str,
        help="Text description of the desired audio style"
    )
    
    parser.add_argument(
        "--duration",
        type=float,
        help="Duration of the video in seconds (required if using --audio-prompt)"
    )
    
    # Image inputs
    parser.add_argument(
        "--characters", "-c",
        nargs="+",
        type=str,
        help="Character image paths (up to 5)"
    )
    
    parser.add_argument(
        "--additional-characters",
        nargs="+",
        type=str,
        help="Additional character image paths (optional)"
    )
    
    parser.add_argument(
        "--backgrounds", "-b",
        nargs="+",
        type=str,
        help="Background image paths (up to 5)"
    )
    
    parser.add_argument(
        "--elements", "-e",
        nargs="+",
        type=str,
        help="Video element image paths (up to 5)"
    )
    
    # Lyrics input (optional for lip sync)
    lyrics_group = parser.add_mutually_exclusive_group()
    lyrics_group.add_argument(
        "--lyrics",
        type=str,
        help="Path to lyrics file"
    )
    lyrics_group.add_argument(
        "--lyrics-text",
        type=str,
        help="Lyrics as text string"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="music_video.mp4",
        help="Output filename (default: music_video.mp4)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./output",
        help="Output directory (default: ./output)"
    )
    
    # Video settings
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Frames per second (default: 30)"
    )
    
    parser.add_argument(
        "--resolution",
        type=str,
        default="1920x1080",
        help="Video resolution as WIDTHxHEIGHT (default: 1920x1080)"
    )
    
    parser.add_argument(
        "--quality",
        type=str,
        choices=["low", "medium", "high"],
        default="high",
        help="Video quality (default: high)"
    )
    
    parser.add_argument(
        "--style",
        type=str,
        default="cinematic",
        help="Video style (default: cinematic)"
    )
    
    # Metadata
    parser.add_argument(
        "--title",
        type=str,
        help="Video title for metadata"
    )
    
    parser.add_argument(
        "--artist",
        type=str,
        help="Artist name for metadata"
    )
    
    # Other options
    parser.add_argument(
        "--no-lip-sync",
        action="store_true",
        help="Disable lip sync even if lyrics are provided"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to JSON configuration file"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without generating video"
    )
    
    return parser.parse_args()


def parse_resolution(resolution_str: str) -> tuple:
    """Parse resolution string to tuple."""
    try:
        width, height = resolution_str.lower().split("x")
        return (int(width), int(height))
    except ValueError:
        logger.error(f"Invalid resolution format: {resolution_str}. Use WIDTHxHEIGHT (e.g., 1920x1080)")
        sys.exit(1)


def load_config_file(config_path: str) -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load config file: {e}")
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    args = parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("THE-PIPE-LINE Music Video Generator")
    logger.info("=" * 40)
    
    # Load config from file if provided
    file_config = {}
    if args.config:
        file_config = load_config_file(args.config)
    
    # Parse resolution
    resolution = parse_resolution(args.resolution)
    
    # Create pipeline config
    config = PipelineConfig(
        fps=file_config.get("fps", args.fps),
        resolution=file_config.get("resolution", resolution),
        quality=file_config.get("quality", args.quality),
        output_dir=file_config.get("output_dir", args.output_dir),
        output_filename=args.output,
        style=file_config.get("style", args.style),
        enable_lip_sync=not args.no_lip_sync
    )
    
    # Create pipeline
    pipeline = MusicVideoPipeline(config=config)
    
    # Add audio input
    if args.audio:
        pipeline.add_audio(file_path=args.audio)
    else:
        if not args.duration:
            logger.error("--duration is required when using --audio-prompt")
            sys.exit(1)
        pipeline.add_audio(
            prompt_description=args.audio_prompt,
            duration_seconds=args.duration
        )
    
    # Add character images
    if args.characters:
        pipeline.add_character_images(
            args.characters,
            args.additional_characters
        )
    
    # Add background images
    if args.backgrounds:
        pipeline.add_background_images(args.backgrounds)
    
    # Add element images
    if args.elements:
        pipeline.add_element_images(args.elements)
    
    # Add lyrics
    if args.lyrics:
        pipeline.add_lyrics(file_path=args.lyrics)
    elif args.lyrics_text:
        pipeline.add_lyrics(text=args.lyrics_text)
    
    # Show input summary
    logger.info("Input Summary:")
    summary = pipeline.get_input_summary()
    logger.info(json.dumps(summary, indent=2))
    
    # Dry run - just validate
    if args.dry_run:
        try:
            pipeline.validate_inputs()
            logger.info("Dry run complete - all inputs are valid!")
            return 0
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return 1
    
    # Create metadata
    metadata = None
    if args.title or args.artist:
        metadata = ExportMetadata(
            title=args.title or "Music Video",
            artist=args.artist or ""
        )
    
    # Run pipeline
    try:
        result = pipeline.run(metadata=metadata)
        
        if result.success:
            logger.info("=" * 40)
            logger.info("VIDEO GENERATION SUCCESSFUL!")
            logger.info(f"Output: {result.output_path}")
            logger.info(f"Execution time: {result.execution_time:.2f}s")
            return 0
        else:
            logger.error("Video generation failed!")
            for error in result.errors:
                logger.error(f"  - {error}")
            return 1
            
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
