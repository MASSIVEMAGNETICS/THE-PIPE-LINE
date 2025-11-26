# THE-PIPE-LINE

**End-to-End Music Video Generation Pipeline**

A comprehensive Python pipeline for generating music videos from user inputs including audio, character images, background images, video elements, and optional lyrics for lip-sync.

## 🎵 Features

- **Audio Input**: Accept song files (MP3, WAV, FLAC, etc.) or text prompts describing the desired audio style
- **Character Images**: Input up to 5 primary character images + optional additional character images
- **Background Images**: Input up to 5 background/scene images
- **Video Elements**: Input up to 5 prop/element images for video composition
- **Lyrics Support**: Optional lyrics input for improved lip-sync capabilities
- **AI Orchestration**: Intelligent scene planning and video composition
- **MP4 Export**: High-quality video export with customizable settings

## 📋 Requirements

- Python 3.8 or higher
- No external dependencies required for core functionality

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/MASSIVEMAGNETICS/THE-PIPE-LINE.git
cd THE-PIPE-LINE

# Install in development mode (optional)
pip install -e .
```

### Basic Usage

```python
from src.pipeline import MusicVideoPipeline

# Create the pipeline
pipeline = MusicVideoPipeline()

# Add your inputs
pipeline.add_audio(file_path="path/to/song.mp3")
pipeline.add_character_images(["character1.png", "character2.png"])
pipeline.add_background_images(["background1.jpg", "background2.jpg"])
pipeline.add_element_images(["element1.png"])
pipeline.add_lyrics(text="Your song lyrics here...")

# Generate the video
result = pipeline.run()

if result.success:
    print(f"Video saved to: {result.output_path}")
```

### Command Line Interface

```bash
# Basic usage
python -m src.cli --audio song.mp3 --characters char.png --output video.mp4

# Full example with all inputs
python -m src.cli \
    --audio song.mp3 \
    --characters char1.png char2.png char3.png \
    --backgrounds bg1.jpg bg2.jpg \
    --elements prop1.png prop2.png \
    --lyrics lyrics.txt \
    --output my_music_video.mp4 \
    --quality high \
    --fps 30

# Using audio prompt instead of file
python -m src.cli \
    --audio-prompt "upbeat electronic dance track" \
    --duration 180 \
    --characters performer.png \
    --output generated_video.mp4
```

### Convenience Function

```python
from src.pipeline import generate_music_video

result = generate_music_video(
    audio_file="song.mp3",
    character_images=["char1.png", "char2.png"],
    background_images=["bg1.jpg"],
    element_images=["element.png"],
    lyrics="Your lyrics here...",
    output_path="./output",
    output_filename="my_video.mp4",
    quality="high"
)
```

## 📁 Project Structure

```
THE-PIPE-LINE/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── input_handlers.py     # Input handling (audio, images, lyrics)
│   ├── ai_orchestrator.py    # AI-powered scene planning
│   ├── video_generator.py    # Video generation and composition
│   ├── exporter.py           # MP4 export and saving
│   ├── pipeline.py           # Main pipeline orchestration
│   └── cli.py                # Command-line interface
├── tests/
│   ├── test_input_handlers.py
│   ├── test_ai_orchestrator.py
│   ├── test_video_generator.py
│   ├── test_exporter.py
│   └── test_pipeline.py
├── config/
│   └── default.json          # Default configuration
├── examples/
│   ├── README.md
│   └── basic_example.py
├── pyproject.toml            # Project configuration
├── .gitignore
└── README.md
```

## 🔧 Configuration

### Pipeline Configuration

```python
from src.pipeline import MusicVideoPipeline, PipelineConfig

config = PipelineConfig(
    fps=30,                        # Frames per second
    resolution=(1920, 1080),       # Video resolution
    quality="high",                # low, medium, high
    output_dir="./output",         # Output directory
    output_filename="video.mp4",   # Output filename
    style="cinematic",             # Video style
    enable_lip_sync=True           # Enable lip sync when lyrics provided
)

pipeline = MusicVideoPipeline(config=config)
```

### JSON Configuration

```json
{
    "fps": 30,
    "resolution": [1920, 1080],
    "quality": "high",
    "output_dir": "./output",
    "output_filename": "music_video.mp4",
    "style": "cinematic",
    "enable_lip_sync": true
}
```

## 📥 Input Types

### Audio Input
- **File formats**: MP3, WAV, FLAC, AAC, OGG, M4A
- **Alternative**: Text prompt describing desired audio style with duration

### Image Inputs
- **Formats**: JPG, JPEG, PNG, GIF, BMP, WEBP
- **Character images**: Up to 5 primary + unlimited additional
- **Background images**: Up to 5
- **Element images**: Up to 5

### Lyrics Input (Optional)
- Plain text lyrics
- File-based lyrics
- Timed lyrics with timestamps for precise lip-sync

## 📤 Output

- **Format**: MP4 (primary), also supports WEBM, MOV, AVI
- **Metadata**: Embedded title, artist, and other metadata
- **Verification**: Checksum verification for file integrity

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_pipeline.py -v

# Run with coverage
pip install pytest-cov
pytest tests/ --cov=src
```

## 📖 API Reference

### MusicVideoPipeline

The main class for orchestrating music video generation.

**Methods:**
- `add_audio(file_path, prompt_description, duration_seconds)` - Add audio input
- `add_character_image(path, is_additional)` - Add a character image
- `add_character_images(paths, additional_paths)` - Add multiple character images
- `add_background_image(path)` - Add a background image
- `add_background_images(paths)` - Add multiple background images
- `add_element_image(path)` - Add a video element image
- `add_element_images(paths)` - Add multiple element images
- `add_lyrics(text, file_path, timestamps)` - Add lyrics for lip-sync
- `run(output_filename, metadata)` - Run the pipeline
- `validate_inputs()` - Validate all inputs
- `get_input_summary()` - Get summary of current inputs
- `reset()` - Reset pipeline to initial state

### PipelineResult

Contains the result of a pipeline run.

**Attributes:**
- `success` - Whether generation was successful
- `output_path` - Path to generated video
- `export_result` - Export details
- `generation_progress` - Generation progress info
- `errors` - List of any errors
- `execution_time` - Total execution time

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
