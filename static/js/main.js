// Main JavaScript for Snow's Spoiled Gifts

document.addEventListener('DOMContentLoaded', function() {

    // ===================================
    // Dark Mode Toggle
    // ===================================
    const darkModeToggle = document.getElementById('darkModeToggle');
    const htmlElement = document.documentElement;

    // Check for saved dark mode preference or default to light mode
    const currentTheme = localStorage.getItem('theme') || 'light';
    if (currentTheme === 'dark') {
        htmlElement.setAttribute('data-theme', 'dark');
        if (darkModeToggle) {
            darkModeToggle.checked = true;
        }
    }

    // Toggle dark mode
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                htmlElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            } else {
                htmlElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
            }
        });
    }

    // ===================================
    // Navbar Scroll Effect
    // ===================================
    const navbar = document.getElementById('mainNav');

    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // ===================================
    // Smooth Scrolling for Anchor Links
    // ===================================
    const navLinks = document.querySelectorAll('a[href^="#"]');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                const navHeight = navbar.offsetHeight;
                const targetPosition = targetSection.offsetTop - navHeight;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                    bsCollapse.hide();
                }
            }
        });
    });

    // ===================================
    // Fade-in Animation on Scroll
    // ===================================
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements
    const animateElements = document.querySelectorAll('.category-card, .gallery-item, .contact-card');
    animateElements.forEach(el => {
        observer.observe(el);
    });

    // ===================================
    // Gallery Lightbox (Simple)
    // ===================================
    const galleryItems = document.querySelectorAll('.gallery-item');

    galleryItems.forEach(item => {
        item.addEventListener('click', function() {
            const img = this.querySelector('img');
            if (img) {
                // Create modal for image viewing
                const modal = document.createElement('div');
                modal.className = 'gallery-modal';
                modal.innerHTML = `
                    <div class="gallery-modal-content">
                        <span class="gallery-close">&times;</span>
                        <img src="${img.src}" alt="${img.alt}">
                    </div>
                `;

                document.body.appendChild(modal);
                document.body.style.overflow = 'hidden';

                // Close modal
                const closeBtn = modal.querySelector('.gallery-close');
                closeBtn.addEventListener('click', function() {
                    document.body.removeChild(modal);
                    document.body.style.overflow = '';
                });

                // Close on background click
                modal.addEventListener('click', function(e) {
                    if (e.target === modal) {
                        document.body.removeChild(modal);
                        document.body.style.overflow = '';
                    }
                });
            }
        });
    });

    // ===================================
    // Form Validation Enhancement
    // ===================================
    const signupForm = document.getElementById('signupForm');

    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            const nameInput = signupForm.querySelector('input[name="name"]');
            const emailInput = signupForm.querySelector('input[name="email"]');

            let isValid = true;

            // Remove previous error states
            nameInput.classList.remove('is-invalid');
            emailInput.classList.remove('is-invalid');

            // Validate name
            if (!nameInput.value.trim() || nameInput.value.trim().length < 2) {
                nameInput.classList.add('is-invalid');
                isValid = false;
            }

            // Validate email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailInput.value.trim() || !emailRegex.test(emailInput.value)) {
                emailInput.classList.add('is-invalid');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // ===================================
    // Auto-hide Flash Messages
    // ===================================
    const flashMessages = document.querySelectorAll('.flash-messages .alert');

    flashMessages.forEach(message => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getInstance(message) || new bootstrap.Alert(message);
            bsAlert.close();
        }, 5000); // Auto-hide after 5 seconds
    });

    // ===================================
    // Category Cards Hover Effect Enhancement
    // ===================================
    const categoryCards = document.querySelectorAll('.category-card');

    categoryCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });

    // ===================================
    // Console Easter Egg
    // ===================================
    console.log('%cSnow\'s Spoiled Gifts', 'font-size: 24px; font-weight: bold; color: #6366f1;');
    console.log('%cComing Soon! 🎁', 'font-size: 16px; color: #ec4899;');
    console.log('%cBuilt with ❤️ using Flask & Bootstrap', 'font-size: 12px; color: #6b7280;');

});

// ===================================
// Gallery Modal Styles (Injected)
// ===================================
const style = document.createElement('style');
style.textContent = `
    .gallery-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease;
    }

    .gallery-modal-content {
        position: relative;
        max-width: 90%;
        max-height: 90%;
    }

    .gallery-modal-content img {
        max-width: 100%;
        max-height: 90vh;
        object-fit: contain;
        border-radius: 8px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }

    .gallery-close {
        position: absolute;
        top: -40px;
        right: 0;
        color: white;
        font-size: 40px;
        font-weight: bold;
        cursor: pointer;
        transition: 0.3s;
    }

    .gallery-close:hover {
        color: #6366f1;
        transform: rotate(90deg);
    }
`;
document.head.appendChild(style);
