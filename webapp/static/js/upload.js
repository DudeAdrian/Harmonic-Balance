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

    // Form submission with fetch()
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent normal form submission
        
        if (!selectedFile) {
            alert('Please select an image first');
            return;
        }

        // Show loading overlay
        loadingOverlay.hidden = false;
        updateLoadingProgress(5, 'Uploading image...');

        // Create FormData and append the file
        const formData = new FormData();
        formData.append('image', selectedFile);

        try {
            // Use XMLHttpRequest for progress tracking
            const xhr = new XMLHttpRequest();
            
            // Track upload progress
            xhr.upload.addEventListener('progress', (event) => {
                if (event.lengthComputable) {
                    const percentComplete = Math.round((event.loaded / event.total) * 100);
                    updateLoadingProgress(percentComplete * 0.3, 'Uploading image...'); // Upload is 30% of total
                }
            });

            // Handle response
            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    // Server responded with redirect or success
                    updateLoadingProgress(100, 'Complete!');
                    
                    // Check if response is a redirect
                    const responseUrl = xhr.responseURL;
                    if (responseUrl && responseUrl.includes('/results/')) {
                        window.location.href = responseUrl;
                    } else if (xhr.getResponseHeader('Content-Type')?.includes('json')) {
                        // JSON response - check for redirect
                        try {
                            const data = JSON.parse(xhr.responseText);
                            if (data.redirect) {
                                window.location.href = data.redirect;
                            } else if (data.error) {
                                alert('Error: ' + data.error);
                                loadingOverlay.hidden = true;
                            }
                        } catch (e) {
                            // Not JSON, might be HTML redirect
                            document.open();
                            document.write(xhr.responseText);
                            document.close();
                        }
                    } else {
                        // HTML response - likely a redirect page
                        document.open();
                        document.write(xhr.responseText);
                        document.close();
                    }
                } else {
                    alert('Upload failed. Please try again.');
                    loadingOverlay.hidden = true;
                }
            });

            xhr.addEventListener('error', () => {
                alert('Network error. Please check your connection and try again.');
                loadingOverlay.hidden = true;
            });

            xhr.addEventListener('abort', () => {
                loadingOverlay.hidden = true;
            });

            // Simulate server-side progress after upload completes
            xhr.addEventListener('loadstart', () => {
                // After upload starts, simulate the server processing stages
                const stages = [
                    { progress: 35, message: 'Analyzing sketch...' },
                    { progress: 45, message: 'Detecting typology...' },
                    { progress: 55, message: 'Generating geometry...' },
                    { progress: 65, message: 'Running compliance checks...' },
                    { progress: 75, message: 'Optimizing acoustics (7.83 Hz)...' },
                    { progress: 85, message: 'Generating G-code...' },
                    { progress: 92, message: 'Creating 3D preview...' },
                    { progress: 98, message: 'Finalizing...' }
                ];

                let stageIndex = 0;
                const progressInterval = setInterval(() => {
                    if (stageIndex < stages.length && !loadingOverlay.hidden) {
                        const stage = stages[stageIndex];
                        updateLoadingProgress(stage.progress, stage.message);
                        stageIndex++;
                    } else {
                        clearInterval(progressInterval);
                    }
                }, 1200); // Update every 1.2 seconds during processing
            });

            // Send the request
            xhr.open('POST', '/upload', true);
            xhr.send(formData);

        } catch (error) {
            console.error('Upload error:', error);
            alert('An error occurred during upload. Please try again.');
            loadingOverlay.hidden = true;
        }
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
