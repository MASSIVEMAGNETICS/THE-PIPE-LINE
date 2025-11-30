# Example usage of THE-PIPE-LINE

This directory contains example files and usage patterns for the music video generation pipeline.

## Quick Start

```python
from src.pipeline import MusicVideoPipeline

# Create pipeline
pipeline = MusicVideoPipeline()

# Add inputs
pipeline.add_audio(file_path="path/to/song.mp3")
pipeline.add_character_images(["char1.png", "char2.png"])
pipeline.add_background_images(["bg1.jpg", "bg2.jpg"])
pipeline.add_element_images(["element1.png"])
pipeline.add_lyrics(text="Your song lyrics here...")

# Run generation
result = pipeline.run()

print(f"Video saved to: {result.output_path}")
```

## Command Line Usage

```bash
# Basic usage
python -m src.cli --audio song.mp3 --characters char.png --output video.mp4

# Full example
python -m src.cli \
    --audio song.mp3 \
    --characters char1.png char2.png char3.png \
    --backgrounds bg1.jpg bg2.jpg \
    --elements prop1.png prop2.png \
    --lyrics lyrics.txt \
    --output my_music_video.mp4
```
