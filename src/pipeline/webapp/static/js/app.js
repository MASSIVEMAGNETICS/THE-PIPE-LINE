/**
 * THE-PIPE-LINE - Next-Gen AI Music Video Generator
 * Frontend JavaScript Application
 * © 2024 MASSIVEMAGNETICS
 */

// ====== State Management ======
const state = {
    uploadedFiles: {
        character: [],
        additional: null,
        background: [],
        element: []
    },
    currentJobId: null,
    pollInterval: null
};

// ====== DOM Elements ======
const elements = {
    form: document.getElementById('videoForm'),
    generateBtn: document.getElementById('generateBtn'),
    progressSection: document.getElementById('progressSection'),
    resultSection: document.getElementById('resultSection'),
    settingsSection: document.querySelector('.settings-section'),
    progressFill: document.getElementById('progressFill'),
    progressPercent: document.getElementById('progressPercent'),
    progressMessage: document.getElementById('progressMessage'),
    progressStages: document.getElementById('progressStages'),
    downloadBtn: document.getElementById('downloadBtn'),
    newVideoBtn: document.getElementById('newVideoBtn'),
    resultDetails: document.getElementById('resultDetails'),
    helpBtn: document.getElementById('helpBtn'),
    helpModal: document.getElementById('helpModal'),
    closeHelp: document.getElementById('closeHelp'),
    duration: document.getElementById('duration'),
    durationValue: document.getElementById('durationValue'),
    fps: document.getElementById('fps'),
    fpsValue: document.getElementById('fpsValue')
};

// ====== Upload Handlers ======
function initializeUploadZones() {
    // Character images
    setupUploadZone('characterUpload', 'characterInput', 'characterPreview', 'character', 5);
    
    // Additional character
    setupUploadZone('additionalCharUpload', 'additionalCharInput', 'additionalCharPreview', 'additional', 1);
    
    // Background images
    setupUploadZone('backgroundUpload', 'backgroundInput', 'backgroundPreview', 'background', 5);
    
    // Element images
    setupUploadZone('elementUpload', 'elementInput', 'elementPreview', 'element', 5);
}

function setupUploadZone(zoneId, inputId, previewId, type, maxFiles) {
    const zone = document.getElementById(zoneId);
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    
    // Click to upload
    zone.addEventListener('click', () => input.click());
    
    // Drag and drop
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });
    
    zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
    });
    
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files, type, maxFiles, preview);
    });
    
    // File input change
    input.addEventListener('change', (e) => {
        handleFiles(e.target.files, type, maxFiles, preview);
    });
}

async function handleFiles(files, type, maxFiles, preview) {
    const fileArray = Array.from(files);
    
    for (const file of fileArray) {
        if (!file.type.startsWith('image/')) {
            showNotification('Please upload image files only', 'error');
            continue;
        }
        
        if (type === 'additional') {
            // Single file for additional character
            await uploadFile(file, type, preview, true);
        } else {
            // Multiple files
            if (state.uploadedFiles[type].length >= maxFiles) {
                showNotification(`Maximum ${maxFiles} files allowed`, 'warning');
                return;
            }
            await uploadFile(file, type, preview, false);
        }
    }
}

async function uploadFile(file, type, preview, single) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (single) {
                state.uploadedFiles[type] = data.path;
            } else {
                state.uploadedFiles[type].push(data.path);
            }
            
            addPreviewItem(preview, file, type, data.path, single);
            showNotification('File uploaded successfully', 'success');
        } else {
            showNotification(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showNotification('Upload failed: ' + error.message, 'error');
    }
}

function addPreviewItem(preview, file, type, path, single) {
    if (single) {
        preview.innerHTML = '';
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
        const item = document.createElement('div');
        item.className = 'preview-item';
        item.innerHTML = `
            <img src="${e.target.result}" alt="${file.name}">
            <button class="remove-btn" data-path="${path}" data-type="${type}">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        item.querySelector('.remove-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            removeFile(path, type, item, single);
        });
        
        preview.appendChild(item);
    };
    reader.readAsDataURL(file);
}

function removeFile(path, type, item, single) {
    if (single) {
        state.uploadedFiles[type] = null;
    } else {
        state.uploadedFiles[type] = state.uploadedFiles[type].filter(p => p !== path);
    }
    item.remove();
}

// ====== Form Submission ======
async function handleSubmit(e) {
    e.preventDefault();
    
    const songPrompt = document.getElementById('songPrompt').value.trim();
    if (!songPrompt) {
        showNotification('Please enter a song description', 'error');
        return;
    }
    
    // Collect form data
    const formData = {
        song_prompt: songPrompt,
        lyrics: document.getElementById('lyrics').value.trim() || null,
        character_images: state.uploadedFiles.character,
        additional_character_image: state.uploadedFiles.additional,
        background_images: state.uploadedFiles.background,
        element_images: state.uploadedFiles.element,
        duration: parseInt(elements.duration.value),
        fps: parseInt(elements.fps.value),
        resolution: document.getElementById('resolution').value,
        compute_mode: document.getElementById('computeMode').value,
        model_backend: document.getElementById('modelBackend').value,
        render_quality: document.getElementById('renderQuality').value
    };
    
    // Start generation
    try {
        elements.generateBtn.disabled = true;
        elements.generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.currentJobId = data.job_id;
            showProgressSection();
            startPolling();
        } else {
            showNotification(data.error || 'Failed to start generation', 'error');
            resetGenerateButton();
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
        resetGenerateButton();
    }
}

function resetGenerateButton() {
    elements.generateBtn.disabled = false;
    elements.generateBtn.innerHTML = '<i class="fas fa-rocket"></i> <span>Generate Video</span>';
}

// ====== Progress Tracking ======
function showProgressSection() {
    elements.settingsSection.style.display = 'none';
    elements.resultSection.style.display = 'none';
    elements.progressSection.style.display = 'block';
}

function startPolling() {
    state.pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/job/${state.currentJobId}`);
            const job = await response.json();
            
            updateProgress(job);
            
            if (job.status === 'completed' || job.status === 'failed') {
                clearInterval(state.pollInterval);
                
                if (job.status === 'completed') {
                    showResult(job);
                } else {
                    showNotification('Generation failed: ' + (job.error || 'Unknown error'), 'error');
                    // Reset to settings section on failure
                    elements.progressSection.style.display = 'none';
                    elements.settingsSection.style.display = 'block';
                    resetGenerateButton();
                }
            }
        } catch (error) {
            // Show user-friendly error notification
            showNotification('Connection error. Retrying...', 'warning');
        }
    }, 1000);
}

function updateProgress(job) {
    const progress = job.progress || 0;
    elements.progressFill.style.width = `${progress}%`;
    elements.progressPercent.textContent = `${progress}%`;
    elements.progressMessage.textContent = job.message || 'Processing...';
    
    // Update stages
    const stages = elements.progressStages.querySelectorAll('.stage');
    if (progress >= 20) updateStage(stages[0], 'completed');
    if (progress >= 40) updateStage(stages[1], progress < 70 ? 'active' : 'completed');
    if (progress >= 70) updateStage(stages[2], progress < 90 ? 'active' : 'completed');
    if (progress >= 90) updateStage(stages[3], progress < 100 ? 'active' : 'completed');
}

function updateStage(stage, status) {
    stage.classList.remove('active', 'completed');
    if (status) stage.classList.add(status);
    
    const icon = stage.querySelector('i');
    if (status === 'completed') {
        icon.className = 'fas fa-check-circle';
    } else if (status === 'active') {
        icon.className = 'fas fa-spinner fa-spin';
    }
}

// ====== Result Display ======
function showResult(job) {
    elements.progressSection.style.display = 'none';
    elements.resultSection.style.display = 'block';
    
    // Update result details
    const result = job.result || {};
    const exportDetails = result.export_details || {};
    const genDetails = result.generation_details || {};
    
    elements.resultDetails.innerHTML = `
        <p><strong>Duration:</strong> <span>${exportDetails.duration_seconds || 0}s</span></p>
        <p><strong>Resolution:</strong> <span>${genDetails.resolution || 'N/A'}</span></p>
        <p><strong>Frame Rate:</strong> <span>${genDetails.fps || 30} FPS</span></p>
        <p><strong>File Size:</strong> <span>${formatBytes(exportDetails.file_size_bytes || 0)}</span></p>
    `;
    
    resetGenerateButton();
}

// ====== Download Handler ======
function handleDownload() {
    if (state.currentJobId) {
        window.location.href = `/api/download/${state.currentJobId}`;
    }
}

function handleNewVideo() {
    // Reset UI
    elements.resultSection.style.display = 'none';
    elements.settingsSection.style.display = 'block';
    
    // Reset form
    elements.form.reset();
    
    // Reset state
    state.uploadedFiles = {
        character: [],
        additional: null,
        background: [],
        element: []
    };
    state.currentJobId = null;
    
    // Clear previews
    document.querySelectorAll('.preview-container').forEach(el => el.innerHTML = '');
    
    // Reset progress stages
    elements.progressStages.querySelectorAll('.stage').forEach(stage => {
        stage.classList.remove('active', 'completed');
        stage.querySelector('i').className = 'fas fa-circle';
    });
    
    elements.progressFill.style.width = '0%';
}

// ====== Compute Mode Buttons ======
function initializePresetButtons() {
    const buttons = document.querySelectorAll('#computeModeButtons .preset-btn');
    const input = document.getElementById('computeMode');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            input.value = btn.dataset.value;
        });
    });
}

// ====== Range Sliders ======
function initializeSliders() {
    elements.duration.addEventListener('input', (e) => {
        elements.durationValue.textContent = `${e.target.value}s`;
    });
    
    elements.fps.addEventListener('input', (e) => {
        elements.fpsValue.textContent = `${e.target.value} FPS`;
    });
}

// ====== Modal ======
function initializeModal() {
    elements.helpBtn.addEventListener('click', () => {
        elements.helpModal.classList.add('active');
    });
    
    elements.closeHelp.addEventListener('click', () => {
        elements.helpModal.classList.remove('active');
    });
    
    elements.helpModal.addEventListener('click', (e) => {
        if (e.target === elements.helpModal) {
            elements.helpModal.classList.remove('active');
        }
    });
}

// ====== Utilities ======
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Style
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#6366f1',
        color: 'white',
        padding: '12px 20px',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        zIndex: '9999',
        boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
        animation: 'slideIn 0.3s ease'
    });
    
    document.body.appendChild(notification);
    
    // Auto remove
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ====== Initialization ======
document.addEventListener('DOMContentLoaded', () => {
    initializeUploadZones();
    initializePresetButtons();
    initializeSliders();
    initializeModal();
    
    // Form submission
    elements.form.addEventListener('submit', handleSubmit);
    
    // Download button
    elements.downloadBtn.addEventListener('click', handleDownload);
    
    // New video button
    elements.newVideoBtn.addEventListener('click', handleNewVideo);
});

// Add notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
