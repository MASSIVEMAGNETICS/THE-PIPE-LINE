#!/usr/bin/env python3
"""
Basic example of using THE-PIPE-LINE for music video generation.
"""

from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import MusicVideoPipeline, PipelineConfig
from src.exporter import ExportMetadata


def main():
    """Run a basic music video generation example."""
    
    print("=" * 60)
    print("THE-PIPE-LINE: Music Video Generation Example")
    print("=" * 60)
    
    # Create a pipeline with custom configuration
    config = PipelineConfig(
        fps=30,
        resolution=(1920, 1080),
        quality="high",
        output_dir="./output",
        output_filename="example_video.mp4",
        style="cinematic"
    )
    
    pipeline = MusicVideoPipeline(config=config)
    
    # Add audio input (using prompt for this example)
    pipeline.add_audio(
        prompt_description="Upbeat electronic dance track with energetic beats",
        duration_seconds=120.0  # 2 minute video
    )
    
    # In a real scenario, you would add actual image files:
    # pipeline.add_character_images([
    #     "path/to/character1.png",
    #     "path/to/character2.png"
    # ])
    # pipeline.add_background_images([
    #     "path/to/background1.jpg",
    #     "path/to/background2.jpg"
    # ])
    # pipeline.add_element_images([
    #     "path/to/element1.png"
    # ])
    
    # Add lyrics for lip sync (optional)
    pipeline.add_lyrics(
        text="""
        Verse 1:
        Dancing through the night
        Stars are shining bright
        
        Chorus:
        Feel the rhythm, feel the beat
        Moving to the sound so sweet
        """
    )
    
    # Show input summary
    print("\nInput Summary:")
    summary = pipeline.get_input_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Create metadata for the video
    metadata = ExportMetadata(
        title="Example Music Video",
        artist="THE-PIPE-LINE Demo",
        genre="Electronic",
        description="Generated using THE-PIPE-LINE music video pipeline"
    )
    
    # Run the pipeline
    print("\nStarting video generation...")
    result = pipeline.run(metadata=metadata)
    
    # Check results
    if result.success:
        print("\n" + "=" * 60)
        print("VIDEO GENERATION SUCCESSFUL!")
        print("=" * 60)
        print(f"Output file: {result.output_path}")
        print(f"Execution time: {result.execution_time:.2f} seconds")
        
        if result.export_result:
            print(f"File size: {result.export_result.file_size} bytes")
            print(f"Checksum: {result.export_result.checksum}")
    else:
        print("\nGeneration failed!")
        for error in result.errors:
            print(f"  Error: {error}")


if __name__ == "__main__":
    main()
