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
