document.addEventListener('DOMContentLoaded', function() {
    initFormValidation();
    initJobSearch();
    initFileUpload();
    initScrollEffects();
    initTooltips();
});

function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (input.value && !isValidEmail(input.value)) {
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
            }
        });
    });

    const passwordInputs = document.querySelectorAll('input[name="password2"], input[name="confirm_password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const form = input.closest('form');
            const password = form.querySelector('input[name="password"], input[name="new_password"]');
            if (password && input.value !== password.value) {
                input.setCustomValidity('Passwords do not match');
            } else {
                input.setCustomValidity('');
            }
        });
    });
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function initJobSearch() {
    const searchInput = document.querySelector('.job-search-input');
    const searchResults = document.querySelector('.search-results-dropdown');
    
    if (searchInput && searchResults) {
        let debounceTimer;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            const query = this.value.trim();
            
            if (query.length < 2) {
                searchResults.classList.remove('show');
                return;
            }
            
            debounceTimer = setTimeout(() => {
                fetchSearchResults(query, searchResults);
            }, 300);
        });

        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.remove('show');
            }
        });
    }
}

function fetchSearchResults(query, container) {
    fetch(`/jobs/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                container.innerHTML = data.map(job => `
                    <a href="/jobs/${job.id}" class="dropdown-item">
                        <strong>${escapeHtml(job.title)}</strong>
                        <br><small class="text-muted">${escapeHtml(job.company)} - ${escapeHtml(job.location || 'Location not specified')}</small>
                    </a>
                `).join('');
                container.classList.add('show');
            } else {
                container.innerHTML = '<div class="dropdown-item text-muted">No results found</div>';
                container.classList.add('show');
            }
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function initFileUpload() {
    const uploadZone = document.querySelector('.resume-upload-zone');
    const fileInput = document.querySelector('input[type="file"][name="resume"]');
    
    if (uploadZone && fileInput) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => uploadZone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => uploadZone.classList.remove('dragover'), false);
        });

        uploadZone.addEventListener('drop', function(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateFileDisplay(files[0]);
            }
        });

        uploadZone.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                updateFileDisplay(this.files[0]);
            }
        });
    }
}

function updateFileDisplay(file) {
    const uploadZone = document.querySelector('.resume-upload-zone');
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    
    if (!allowedTypes.includes(file.type)) {
        alert('Please upload a PDF or DOCX file.');
        return;
    }

    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('File size must be less than 16MB.');
        return;
    }
    
    if (uploadZone) {
        const icon = file.type === 'application/pdf' ? 'fa-file-pdf text-danger' : 'fa-file-word text-primary';
        uploadZone.innerHTML = `
            <i class="fas ${icon} fa-3x mb-3"></i>
            <h5>${escapeHtml(file.name)}</h5>
            <p class="text-muted mb-0">${formatFileSize(file.size)}</p>
            <small class="text-success"><i class="fas fa-check-circle me-1"></i>Ready to upload</small>
        `;
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function initScrollEffects() {
    const navbar = document.querySelector('.navbar');
    
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('shadow-lg');
            } else {
                navbar.classList.remove('shadow-lg');
            }
        });
    }

    const fadeElements = document.querySelectorAll('.fade-on-scroll');
    
    if (fadeElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, { threshold: 0.1 });
        
        fadeElements.forEach(el => observer.observe(el));
    }
}

function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

function showLoading(button) {
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="loading-spinner me-2"></span>Loading...';
    return originalText;
}

function hideLoading(button, originalText) {
    button.disabled = false;
    button.innerHTML = originalText;
}
