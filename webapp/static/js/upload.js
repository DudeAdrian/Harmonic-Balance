/**
 * Harmonic Habitats Web Application - Upload JavaScript
 * Handles drag-and-drop, image preview, and upload progress
 */

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const uploadZone = document.getElementById('upload-zone');
    const imageInput = document.getElementById('image-input');
    const uploadContent = document.getElementById('upload-content');
    const imagePreview = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');
    const removeBtn = document.getElementById('remove-btn');
    const generateBtn = document.getElementById('generate-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingStatus = document.getElementById('loading-status');
    const progressFill = document.getElementById('progress-fill');

    let selectedFile = null;

    // Drag and drop handlers
    uploadZone.addEventListener('click', () => imageInput.click());

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // File input change
    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Remove button
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFile();
    });

    // Handle file selection
    function handleFileSelect(file) {
        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];
        const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'];
        
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        const isValidType = allowedTypes.includes(file.type) || allowedExtensions.includes(fileExtension);
        
        if (!isValidType) {
            alert('Please select a valid image file (JPG, PNG, GIF, WEBP, or BMP)');
            return;
        }

        // Validate file size (16MB)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('File is too large. Maximum size is 16MB.');
            return;
        }

        selectedFile = file;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            uploadContent.hidden = true;
            imagePreview.hidden = false;
            generateBtn.disabled = false;
        };
        reader.readAsDataURL(file);

        // Update file input
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        imageInput.files = dataTransfer.files;
    }

    // Clear selected file
    function clearFile() {
        selectedFile = null;
        imageInput.value = '';
        previewImg.src = '';
        uploadContent.hidden = false;
        imagePreview.hidden = true;
        generateBtn.disabled = true;
    }

    // Form submission
    uploadForm.addEventListener('submit', async (e) => {
        if (!selectedFile) {
            e.preventDefault();
            alert('Please select an image first');
            return;
        }

        // Show loading overlay
        loadingOverlay.hidden = false;
        updateLoadingProgress(0);

        // Simulate progress updates (in production, this would be real progress)
        const stages = [
            { progress: 10, message: 'Analyzing sketch...' },
            { progress: 25, message: 'Detecting typology...' },
            { progress: 40, message: 'Generating geometry...' },
            { progress: 55, message: 'Running compliance checks...' },
            { progress: 70, message: 'Optimizing acoustics (7.83 Hz)...' },
            { progress: 85, message: 'Generating G-code...' },
            { progress: 95, message: 'Creating 3D preview...' },
            { progress: 100, message: 'Finalizing...' }
        ];

        let stageIndex = 0;
        const progressInterval = setInterval(() => {
            if (stageIndex < stages.length) {
                const stage = stages[stageIndex];
                updateLoadingProgress(stage.progress, stage.message);
                stageIndex++;
            } else {
                clearInterval(progressInterval);
            }
        }, 800);

        // Form will submit normally, loading overlay shows during page transition
    });

    // Update loading progress
    function updateLoadingProgress(progress, message) {
        if (progressFill) {
            progressFill.style.width = progress + '%';
        }
        if (message && loadingStatus) {
            loadingStatus.textContent = message;
        }
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Escape to clear selection
        if (e.key === 'Escape' && selectedFile) {
            clearFile();
        }
    });

    // Prevent accidental navigation during upload
    window.addEventListener('beforeunload', (e) => {
        if (!loadingOverlay.hidden) {
            e.preventDefault();
            e.returnValue = 'Generation in progress. Are you sure you want to leave?';
        }
    });

    // Console welcome message
    console.log('%c🏛️ Harmonic Habitats', 'font-size: 24px; font-weight: bold; color: #8B5A2B;');
    console.log('%cSacred Geometry Engine v0.1.0', 'font-size: 14px; color: #666;');
    console.log('Ready to transform sketches into resonant dwellings.');
});
