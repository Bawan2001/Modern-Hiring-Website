// JobSphere - Main JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navUl = document.querySelector('nav ul');

    if (mobileMenuBtn && navUl) {
        mobileMenuBtn.addEventListener('click', function () {
            navUl.classList.toggle('mobile-open');
        });
    }

    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            msg.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(function () { msg.remove(); }, 300);
        }, 5000);
    });

    // File input display
    const fileInputs = document.querySelectorAll('.file-input');
    fileInputs.forEach(function (input) {
        input.addEventListener('change', function () {
            const label = this.closest('.file-upload-area').querySelector('.file-upload-label span:first-child');
            if (this.files.length > 0) {
                label.textContent = '📎 ' + this.files[0].name;
            }
        });
    });

    // Form validation feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        const inputs = form.querySelectorAll('.form-control');
        inputs.forEach(function (input) {
            input.addEventListener('blur', function () {
                if (this.required && !this.value.trim()) {
                    this.style.borderColor = 'var(--accent)';
                } else {
                    this.style.borderColor = '';
                }
            });
        });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });

    // CSRF token for AJAX requests
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    if (csrfToken) {
        window.csrfToken = csrfToken.getAttribute('content');
    }
});

// Utility: Show toast notification
function showToast(message, type = 'info') {
    const container = document.querySelector('.flash-container') || createFlashContainer();
    const toast = document.createElement('div');
    toast.className = `flash-message flash-${type}`;
    toast.innerHTML = `<span>${message}</span><button class="flash-close" onclick="this.parentElement.remove()">×</button>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-container';
    document.body.appendChild(container);
    return container;
}

// Add slide out animation
const style = document.createElement('style');
style.textContent = '@keyframes slideOut { from { opacity: 1; transform: translateX(0); } to { opacity: 0; transform: translateX(100px); } }';
document.head.appendChild(style);
