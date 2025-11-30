"""
🚀 THE-PIPE-LINE Web Application Server 🚀

Production-ready Flask web application for the AI Music Video Generation Pipeline.
Supports both web deployment and Windows 10 desktop mode.
"""

import os
import json
import uuid
import threading
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import asdict

from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename

# Import pipeline components
from ..main import MusicVideoPipeline
from ..input_handler import PipelineInput, create_input_from_dict
from ..orchestrator import ComputeMode, ModelBackend
from ..video_generator import RenderQuality


# Initialize Flask app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'the-pipe-line-secret-key-2024')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp(prefix='pipeline_uploads_')
app.config['OUTPUT_FOLDER'] = tempfile.mkdtemp(prefix='pipeline_outputs_')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

# Thread-safe job storage with lock
# NOTE: For production scale, use Redis or a database
_jobs_lock = threading.Lock()
jobs = {}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_job_status(job_id: str) -> dict:
    """Get job status by ID (thread-safe)."""
    with _jobs_lock:
        return jobs.get(job_id, {"status": "not_found", "error": "Job not found"}).copy()


def update_job(job_id: str, updates: dict) -> None:
    """Update job status (thread-safe)."""
    with _jobs_lock:
        if job_id in jobs:
            jobs[job_id].update(updates)


def run_pipeline_job(job_id: str, input_data: dict, settings: dict):
    """Run pipeline job in background thread."""
    try:
        update_job(job_id, {"status": "running", "progress": 10, "message": "Initializing pipeline..."})
        
        # Parse settings
        compute_mode_map = {
            "ultra_low": ComputeMode.ULTRA_LOW,
            "balanced": ComputeMode.BALANCED,
            "quality": ComputeMode.QUALITY,
            "turbo": ComputeMode.TURBO
        }
        model_backend_map = {
            "local_fast": ModelBackend.LOCAL_FAST,
            "local_quality": ModelBackend.LOCAL_QUALITY,
            "cloud_api": ModelBackend.CLOUD_API,
            "hybrid": ModelBackend.HYBRID
        }
        render_quality_map = {
            "preview": RenderQuality.PREVIEW,
            "draft": RenderQuality.DRAFT,
            "standard": RenderQuality.STANDARD,
            "high": RenderQuality.HIGH
        }
        
        compute_mode = compute_mode_map.get(settings.get('compute_mode', 'balanced'), ComputeMode.BALANCED)
        model_backend = model_backend_map.get(settings.get('model_backend', 'local_fast'), ModelBackend.LOCAL_FAST)
        render_quality = render_quality_map.get(settings.get('render_quality', 'standard'), RenderQuality.STANDARD)
        
        # Parse resolution
        resolution_str = settings.get('resolution', '1920x1080')
        try:
            width, height = resolution_str.split('x')
            resolution = (int(width), int(height))
        except ValueError:
            resolution = (1920, 1080)
        
        update_job(job_id, {"progress": 20, "message": "Creating pipeline instance..."})
        
        # Create pipeline
        output_dir = app.config['OUTPUT_FOLDER']
        pipeline = MusicVideoPipeline(
            target_duration=float(settings.get('duration', 60)),
            fps=int(settings.get('fps', 30)),
            resolution=resolution,
            output_dir=output_dir,
            compute_mode=compute_mode,
            model_backend=model_backend,
            render_quality=render_quality
        )
        
        update_job(job_id, {"progress": 30, "message": "Processing inputs..."})
        
        # Create pipeline input
        pipeline_input = create_input_from_dict(input_data)
        
        update_job(job_id, {"progress": 40, "message": "🎬 Orchestrating AI models..."})
        
        # Run pipeline
        output_filename = f"music_video_{job_id}.mp4"
        result = pipeline.run(pipeline_input, output_filename=output_filename, validate_images=False)
        
        update_job(job_id, {"progress": 90, "message": "Finalizing video..."})
        
        if result["success"]:
            update_job(job_id, {
                "status": "completed",
                "progress": 100,
                "message": "✅ Video generated successfully!",
                "result": result,
                "output_path": result["output_path"],
                "completed_at": datetime.now().isoformat()
            })
        else:
            update_job(job_id, {
                "status": "failed",
                "error": result.get("error", "Unknown error"),
                "message": f"❌ Failed: {result.get('error')}"
            })
            
    except Exception as e:
        update_job(job_id, {
            "status": "failed",
            "error": str(e),
            "message": f"❌ Error: {str(e)}"
        })


@app.route('/')
def index():
    """Main application page."""
    return render_template('index.html')


@app.route('/api/health')
def health_check():
    """API health check endpoint."""
    return jsonify({
        "status": "healthy",
        "app": "THE-PIPE-LINE",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        return jsonify({
            "success": True,
            "filename": unique_filename,
            "path": filepath,
            "original_name": filename
        })
    
    return jsonify({"error": "File type not allowed"}), 400


@app.route('/api/generate', methods=['POST'])
def generate_video():
    """Start video generation job."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if not data.get('song_prompt'):
            return jsonify({"error": "Song prompt is required"}), 400
        
        # Create job ID
        job_id = uuid.uuid4().hex[:12]
        
        # Prepare input data
        input_data = {
            "song_prompt": data.get('song_prompt', ''),
            "character_images": data.get('character_images', []),
            "additional_character_image": data.get('additional_character_image'),
            "background_images": data.get('background_images', []),
            "element_images": data.get('element_images', []),
            "lyrics": data.get('lyrics')
        }
        
        # Settings
        settings = {
            "duration": data.get('duration', 60),
            "fps": data.get('fps', 30),
            "resolution": data.get('resolution', '1920x1080'),
            "compute_mode": data.get('compute_mode', 'balanced'),
            "model_backend": data.get('model_backend', 'local_fast'),
            "render_quality": data.get('render_quality', 'standard')
        }
        
        # Initialize job
        jobs[job_id] = {
            "id": job_id,
            "status": "queued",
            "progress": 0,
            "message": "Job queued...",
            "created_at": datetime.now().isoformat(),
            "input_data": input_data,
            "settings": settings
        }
        
        # Start background job
        thread = threading.Thread(
            target=run_pipeline_job,
            args=(job_id, input_data, settings)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "message": "Video generation started"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/job/<job_id>')
def get_job(job_id: str):
    """Get job status."""
    job = get_job_status(job_id)
    return jsonify(job)


@app.route('/api/download/<job_id>')
def download_video(job_id: str):
    """Download generated video."""
    job = get_job_status(job_id)
    
    if job.get("status") != "completed":
        return jsonify({"error": "Video not ready"}), 404
    
    output_path = job.get("output_path")
    if not output_path or not os.path.exists(output_path):
        return jsonify({"error": "Video file not found"}), 404
    
    return send_file(
        output_path,
        mimetype='video/mp4',
        as_attachment=True,
        download_name=f"music_video_{job_id}.mp4"
    )


@app.route('/api/presets')
def get_presets():
    """Get available presets and options."""
    return jsonify({
        "compute_modes": [
            {"value": "ultra_low", "label": "⚡ Ultra Low (Fastest)", "description": "Maximum caching, minimal processing"},
            {"value": "turbo", "label": "🚀 Turbo", "description": "Parallel processing, reduced scenes"},
            {"value": "balanced", "label": "⚖️ Balanced", "description": "Smart trade-off"},
            {"value": "quality", "label": "💎 Quality", "description": "Full processing, best output"}
        ],
        "model_backends": [
            {"value": "local_fast", "label": "🏠 Local Fast", "description": "Lightweight local models"},
            {"value": "local_quality", "label": "🏠 Local Quality", "description": "High-quality local models"},
            {"value": "cloud_api", "label": "☁️ Cloud API", "description": "Cloud AI APIs"},
            {"value": "hybrid", "label": "🔀 Hybrid", "description": "Best of both worlds"}
        ],
        "render_qualities": [
            {"value": "preview", "label": "📱 Preview (360p)", "description": "Ultra-fast preview"},
            {"value": "draft", "label": "📺 Draft (720p)", "description": "Fast draft"},
            {"value": "standard", "label": "🖥️ Standard (1080p)", "description": "Full HD"},
            {"value": "high", "label": "🎬 High (4K)", "description": "Maximum quality"}
        ],
        "resolutions": [
            {"value": "640x360", "label": "360p"},
            {"value": "1280x720", "label": "720p HD"},
            {"value": "1920x1080", "label": "1080p Full HD"},
            {"value": "3840x2160", "label": "4K UHD"}
        ]
    })


def run_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """Run the Flask server.
    
    Args:
        host: Host address to bind to.
        port: Port number to listen on.
        debug: Enable debug mode (WARNING: Never use in production!).
    """
    server_url = f"http://{host}:{port}"
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚀 THE-PIPE-LINE - AI Music Video Generator 🚀             ║
║                                                              ║
║   Next-Gen Multimodel Pipeline with CHEAT CODES!             ║
║                                                              ║
║   Server running at: {server_url:<38}║
║                                                              ║
║   Ready for Windows 10 / Web deployment!                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    # NOTE: debug=True should NEVER be used in production environments
    # as it enables the interactive debugger which can execute arbitrary code
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    # Only enable debug mode when running directly for development
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    run_server(debug=debug_mode)
