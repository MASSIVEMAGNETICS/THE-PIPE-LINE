# THE-PIPE-LINE

🚀 **NEXT-GEN MULTIMODEL AI Music Video Generation Pipeline** 🚀

## Overview

THE-PIPE-LINE is a **revolutionary** end-to-end pipeline for generating music videos using user prompts, images, and AI orchestration. Built with **ultra-low compute optimization** and **multimodel architecture**, it transforms creative inputs into rendered MP4 music videos at blazing speed.

## 🎮 CHEAT CODES - Revolutionary Features

### Low Compute Optimizations
- **CHEAT CODE #1:** Scene fingerprinting & intelligent caching (0 compute for repeated inputs!)
- **CHEAT CODE #2:** Lazy evaluation pipeline (only compute what's needed)
- **CHEAT CODE #3:** Smart analysis caching (instant theme detection)
- **CHEAT CODE #4:** Streaming frame generation (constant memory usage)
- **CHEAT CODE #5:** Frame interpolation (render less, interpolate more - 2-4x speed!)
- **CHEAT CODE #6:** Quality presets for instant speed/quality tradeoffs
- **CHEAT CODE #7:** Multi-model backend selection

### Multimodel Architecture
- **LOCAL_FAST:** Lightweight local models for instant processing
- **LOCAL_QUALITY:** High-quality local models for best output
- **CLOUD_API:** Cloud AI APIs for maximum capabilities
- **HYBRID:** Best of both worlds - smart routing

### Compute Modes
- **ULTRA_LOW:** Maximum caching, minimal processing (fastest!)
- **BALANCED:** Smart trade-off between speed and quality
- **QUALITY:** Full processing for best output
- **TURBO:** Parallel processing with reduced scene count

### Render Quality Presets
- **PREVIEW:** 360p ultra-fast preview (4x frame skip)
- **DRAFT:** 720p fast draft (2x frame skip)
- **STANDARD:** 1080p balanced (full quality)
- **HIGH:** 4K maximum quality

## Features

- **Multimodal Input Support:**
  - Song prompt (text description of the music)
  - Up to 5 character reference images
  - Optional additional character image
  - Up to 5 background reference images
  - Up to 5 element/prop images for video content
  - Optional lyrics input for improved lip syncing

- **AI Orchestration:**
  - Intelligent scene generation based on song analysis
  - Automatic distribution of visual assets across scenes
  - Theme detection and mood analysis
  - Lip sync support when lyrics are provided
  - **Scene caching for instant reuse**

- **Video Output:**
  - High-quality MP4 output format
  - Configurable resolution (360p to 4K)
  - Configurable frame rate (default: 30 fps)
  - Configurable target duration
  - **Frame interpolation for speed boost**

- **Export & Save:**
  - Export to MP4 format
  - Save to custom locations
  - Detailed export metadata

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

## Usage

### Command Line Interface

```bash
# Basic usage with song prompt
music-video-pipeline --song-prompt "A happy upbeat summer song" --skip-validation

# 🎮 TURBO MODE - Ultra-fast preview generation
music-video-pipeline \
  --song-prompt "An epic rock anthem" \
  --compute-mode turbo \
  --render-quality preview \
  --skip-validation

# 🚀 ULTRA LOW COMPUTE - Maximum caching, fastest processing
music-video-pipeline \
  --song-prompt "A chill lo-fi beat" \
  --compute-mode ultra_low \
  --model-backend local_fast \
  --skip-validation

# Full usage with all inputs and next-gen options
music-video-pipeline \
  --song-prompt "An emotional ballad about love and loss" \
  --character-images char1.jpg char2.jpg \
  --additional-character extra.jpg \
  --background-images bg1.jpg bg2.jpg \
  --element-images prop1.jpg \
  --lyrics "These are the lyrics to the song" \
  --output my_video.mp4 \
  --output-dir ./output \
  --duration 120 \
  --fps 30 \
  --resolution 1920x1080 \
  --compute-mode balanced \
  --model-backend hybrid \
  --render-quality standard

# Using a lyrics file
music-video-pipeline \
  --song-prompt "A rock anthem" \
  --lyrics-file lyrics.txt \
  --output rock_video.mp4

# Using JSON input
music-video-pipeline --json-input input.json --output video.mp4
```

### Python API

```python
from pipeline.main import MusicVideoPipeline
from pipeline.input_handler import PipelineInput
from pipeline.orchestrator import ComputeMode, ModelBackend
from pipeline.video_generator import RenderQuality

# 🚀 NEXT-GEN: Create pipeline with CHEAT CODES!
pipeline = MusicVideoPipeline(
    target_duration=60.0,
    fps=30,
    resolution=(1920, 1080),
    output_dir="./output",
    compute_mode=ComputeMode.TURBO,        # 🎮 CHEAT CODE!
    model_backend=ModelBackend.LOCAL_FAST, # Multimodel support
    render_quality=RenderQuality.DRAFT     # 2x speed with interpolation
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

### JSON Input Format

Create a JSON file with your inputs:

```json
{
  "song_prompt": "A beautiful sunset scene with soft music",
  "character_images": ["char1.jpg", "char2.jpg"],
  "additional_character_image": "extra_char.jpg",
  "background_images": ["sunset1.jpg", "sunset2.jpg"],
  "element_images": ["birds.jpg"],
  "lyrics": "As the sun sets low\nColors paint the sky"
}
```

## Pipeline Architecture

The pipeline consists of four main stages:

1. **Input Validation** - Validates all user inputs and image paths
2. **AI Orchestration** - Analyzes inputs and generates scene-by-scene plan
3. **Video Generation** - Renders video frames for each scene
4. **Export** - Assembles scenes and exports final MP4

```
User Inputs → Validation → AI Orchestration → Video Generation → MP4 Export
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=pipeline --cov-report=html
```

### Project Structure

```
THE-PIPE-LINE/
├── src/
│   └── pipeline/
│       ├── __init__.py          # Package initialization
│       ├── main.py              # Main pipeline and CLI
│       ├── input_handler.py     # Input validation and handling
│       ├── orchestrator.py      # AI orchestration logic
│       ├── video_generator.py   # Video frame generation
│       └── exporter.py          # MP4 export functionality
├── tests/
│   ├── test_input_handler.py
│   ├── test_orchestrator.py
│   ├── test_video_generator.py
│   ├── test_exporter.py
│   └── test_pipeline.py
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--song-prompt` | Text description of the song (required) | - |
| `--character-images` | Paths to character images (up to 5) | [] |
| `--additional-character` | Path to extra character image | None |
| `--background-images` | Paths to background images (up to 5) | [] |
| `--element-images` | Paths to element/prop images (up to 5) | [] |
| `--lyrics` | Lyrics text for lip syncing | None |
| `--lyrics-file` | Path to lyrics file | None |
| `--output` | Output MP4 filename | music_video.mp4 |
| `--output-dir` | Output directory | Current directory |
| `--duration` | Target video duration (seconds) | 60.0 |
| `--fps` | Frames per second | 30 |
| `--resolution` | Output resolution (WIDTHxHEIGHT) | 1920x1080 |
| `--json-input` | Path to JSON input file | None |
| `--skip-validation` | Skip image path validation | False |

### 🎮 CHEAT CODE Options

| Option | Description | Default |
|--------|-------------|---------|
| `--compute-mode` | Optimization mode: `ultra_low`, `balanced`, `quality`, `turbo` | balanced |
| `--model-backend` | AI backend: `local_fast`, `local_quality`, `cloud_api`, `hybrid` | local_fast |
| `--render-quality` | Quality preset: `preview` (360p), `draft` (720p), `standard` (1080p), `high` (4K) | standard |

## License

MIT License
