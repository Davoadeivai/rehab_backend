document.addEventListener('DOMContentLoaded', function() {
    const storedTheme = localStorage.getItem('theme');
    const htmlElement = document.querySelector('html');
    const darkModeToggle = document.getElementById('darkModeToggle');

    const getPreferredTheme = () => {
        if (storedTheme) {
            return storedTheme;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    const setTheme = (theme) => {
        htmlElement.setAttribute('data-bs-theme', theme);
    };

    setTheme(getPreferredTheme());

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', newTheme);
            setTheme(newTheme);

            // Update icon
            const icon = darkModeToggle.querySelector('i');
            icon.classList.toggle('fa-moon');
            icon.classList.toggle('fa-sun');
        });

        // Update icon based on current theme
        const updateToggleIcon = () => {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const icon = darkModeToggle.querySelector('i');
            if (currentTheme === 'dark') {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }
        };

        updateToggleIcon();

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            if (storedTheme !== 'light' && storedTheme !== 'dark') {
                setTheme(getPreferredTheme());
                updateToggleIcon();
            }
        });
    }
});
