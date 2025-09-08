// Add loading animation to buttons when clicked
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', function() {
        if (!this.classList.contains('no-loading')) {
            this.classList.add('loading');
            // Remove loading class after animation completes
            setTimeout(() => {
                this.classList.remove('loading');
            }, 1000);
        }
    });
});

// Smooth scroll to top
document.querySelectorAll('.scroll-to-top').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});

// Initialize tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Add fade-in animation to cards
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.card').forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
});

// Add confirmation for delete actions
document.querySelectorAll('[data-confirm]').forEach(element => {
    element.addEventListener('click', function(e) {
        if (!confirm(this.dataset.confirm)) {
            e.preventDefault();
        }
    });
});

// Format numbers with commas
document.querySelectorAll('.format-number').forEach(element => {
    const number = parseInt(element.textContent);
    if (!isNaN(number)) {
        element.textContent = number.toLocaleString('fa-IR');
    }
});

// Add scroll to top button when scrolling down
window.addEventListener('scroll', function() {
    const scrollTopBtn = document.querySelector('.scroll-top-btn');
    if (window.scrollY > 300) {
        scrollTopBtn?.classList.add('show');
    } else {
        scrollTopBtn?.classList.remove('show');
    }
});

// Add active class to current nav item
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}); 