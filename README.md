# THE-PIPE-LINE

<div align="center">

# 🚀 THE-PIPE-LINE 🚀

### Next-Gen AI Music Video Generator

**Production-Ready Desktop & Web Application**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Windows 10](https://img.shields.io/badge/Windows-10+-0078D6.svg)](https://www.microsoft.com/windows)
[![Web Ready](https://img.shields.io/badge/Web-Ready-green.svg)](https://flask.palletsprojects.com/)

*Million-dollar quality • Zero hassle • State-of-the-art AI*

</div>

---

## ✨ Features

### 🖥️ Full Desktop Application
- **Windows 10/11 native support** - Launch from Start Menu
- **macOS & Linux compatible** - Cross-platform
- **Modern glassmorphism UI** - Beautiful, responsive design
- **One-click deployment** - Ready to use out of the box

### 🌐 Web Application
- **Deploy anywhere** - Cloud, on-premise, or localhost
- **REST API** - Full programmatic access
- **Real-time progress** - Live updates via polling
- **Responsive design** - Works on desktop, tablet, mobile

### 🎬 AI Video Generation
- **Multimodal inputs** - Text, images, and lyrics
- **Intelligent scene orchestration** - AI-powered storytelling
- **Multiple quality presets** - 360p to 4K
- **Lip sync support** - When lyrics are provided

### 🎮 CHEAT CODES (Ultra-Low Compute)
- **Scene fingerprinting** - 0 compute for repeated inputs
- **Lazy evaluation** - Only compute what's needed
- **Frame interpolation** - 2-4x speed boost
- **Smart caching** - Instant theme detection

### 🧠 Multimodel Architecture
- **LOCAL_FAST** - Lightweight models for instant results
- **LOCAL_QUALITY** - High-quality local processing
- **CLOUD_API** - Cloud AI for maximum capabilities
- **HYBRID** - Best of both worlds

## Installation

```bash
# Clone the repository
git clone https://github.com/MASSIVEMAGNETICS/THE-PIPE-LINE.git
cd THE-PIPE-LINE

# Install the package
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

---
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

# Install the package
pip install -e .

# For development (includes testing tools)
pip install -e ".[dev]"

# For desktop app with native window support
pip install -e ".[desktop]"

# Install everything
pip install -e ".[all]"
```

### Launch Desktop Application (Windows 10+)

```bash
# Launch the desktop app (opens in browser)
the-pipe-line-desktop

# Or use the GUI launcher
the-pipe-line-gui
```

### Start Web Server

```bash
# Start the web server
the-pipe-line-server

# Server runs at http://localhost:5000
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
the-pipe-line --song-prompt "A happy upbeat summer song" --skip-validation

# 🎮 TURBO MODE - Ultra-fast preview
the-pipe-line --song-prompt "An epic rock anthem" --compute-mode turbo --render-quality preview --skip-validation

# 🚀 Full production quality
the-pipe-line \
  --song-prompt "An emotional ballad about love and loss" \
  --character-images char1.jpg char2.jpg \
  --background-images bg1.jpg bg2.jpg \
  --lyrics "These are the lyrics..." \
  --output my_video.mp4 \
  --resolution 1920x1080 \
  --compute-mode quality \
  --render-quality high
```

---

## 🎨 Web Interface

The web application provides a beautiful, intuitive interface:

- **Drag & Drop** - Upload images easily
- **Real-time Progress** - Watch your video generate
- **Settings Panel** - Fine-tune every aspect
- **Download Ready** - One-click video download

Access at `http://localhost:5000` after starting the server.

---

## 📖 Python API

```python
from pipeline.main import MusicVideoPipeline
from pipeline.input_handler import PipelineInput
from pipeline.orchestrator import ComputeMode, ModelBackend
from pipeline.video_generator import RenderQuality

# 🚀 Create pipeline with CHEAT CODES!
pipeline = MusicVideoPipeline(
    target_duration=60.0,
    fps=30,
    resolution=(1920, 1080),
    output_dir="./output",
    compute_mode=ComputeMode.TURBO,
    model_backend=ModelBackend.LOCAL_FAST,
    render_quality=RenderQuality.STANDARD
)

# Create input
pipeline_input = PipelineInput(
    song_prompt="An upbeat dance track with electronic beats",
    character_images=["character1.jpg", "character2.jpg"],
    background_images=["background.jpg"],
    element_images=["prop1.jpg"],
    lyrics="Dance to the rhythm of the night"
)

# Run pipeline
result = pipeline.run(pipeline_input, output_filename="dance_video.mp4")

if result["success"]:
    print(f"Video created: {result['output_path']}")
    print(f"Duration: {result['export_details']['duration_seconds']}s")
else:
    print(f"Failed: {result['error']}")
```

---

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
│   └── pipeline/
│       ├── __init__.py           # Package initialization
│       ├── main.py               # Main pipeline and CLI
│       ├── desktop.py            # Desktop application launcher
│       ├── input_handler.py      # Input validation
│       ├── orchestrator.py       # AI orchestration
│       ├── video_generator.py    # Video frame generation
│       ├── exporter.py           # MP4 export
│       └── webapp/               # Web application
│           ├── __init__.py
│           ├── app.py            # Flask server
│           ├── templates/        # HTML templates
│           │   └── index.html
│           └── static/           # CSS, JS, images
│               ├── css/
│               ├── js/
│               └── img/
├── tests/                        # Test suite
├── pyproject.toml                # Project configuration
└── README.md                     # This file
```

---

## ⚙️ Configuration Options

### Compute Modes

| Mode | Description | Speed |
|------|-------------|-------|
| `ultra_low` | Maximum caching, minimal processing | ⚡⚡⚡⚡ |
| `turbo` | Parallel processing, reduced scenes | ⚡⚡⚡ |
| `balanced` | Smart trade-off | ⚡⚡ |
| `quality` | Full processing, best output | ⚡ |

### Render Quality

| Preset | Resolution | Frame Skip |
|--------|------------|------------|
| `preview` | 360p | 4x |
| `draft` | 720p | 2x |
| `standard` | 1080p | None |
| `high` | 4K | None |

### Model Backends

| Backend | Description |
|---------|-------------|
| `local_fast` | Lightweight local models |
| `local_quality` | High-quality local models |
| `cloud_api` | Cloud AI APIs |
| `hybrid` | Automatic routing |

---

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=pipeline --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

---

## 📄 License

MIT License - © 2024 MASSIVEMAGNETICS

---

<div align="center">

**Made with ❤️ by MASSIVEMAGNETICS**

*THE-PIPE-LINE - Where AI Meets Creativity*

</div>
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
