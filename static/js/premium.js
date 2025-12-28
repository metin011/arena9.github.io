document.addEventListener('DOMContentLoaded', () => {
    const html = document.documentElement;

    // 1. Theme Persistence Logic
    const initTheme = () => {
        const savedTheme = localStorage.getItem('arena-theme') || 'dark';
        html.setAttribute('data-theme', savedTheme);
        // Compatibility with old Tailwind dark: class
        html.classList.toggle('dark', savedTheme === 'dark');
        updateThemeIcon(savedTheme);
    };

    const updateThemeIcon = (theme) => {
        const themeToggle = document.getElementById('theme-toggle');
        if (!themeToggle) return;

        // Smooth rotation and icon swap
        themeToggle.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            themeToggle.style.transform = 'rotate(0deg)';
        }, 500);
    };

    window.toggleArenaTheme = () => {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        html.setAttribute('data-theme', newTheme);
        html.classList.toggle('dark', newTheme === 'dark');
        localStorage.setItem('arena-theme', newTheme);
        updateThemeIcon(newTheme);
    };

    // 2. Scroll Reveal Animation
    const reveal = () => {
        const reveals = document.querySelectorAll('.reveal');
        for (let i = 0; i < reveals.length; i++) {
            const windowHeight = window.innerHeight;
            const elementTop = reveals[i].getBoundingClientRect().top;
            const elementVisible = 150;
            if (elementTop < windowHeight - elementVisible) {
                reveals[i].classList.add('active');
            }
        }
    };

    window.addEventListener('scroll', reveal);

    // Initial checks
    initTheme();
    reveal();
});
