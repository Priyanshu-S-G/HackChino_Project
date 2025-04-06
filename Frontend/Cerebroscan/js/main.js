document.addEventListener('DOMContentLoaded', function() {
    // Handle scan button click
    const scanBtn = document.querySelector('.scan-btn');
    scanBtn.addEventListener('click', function() {
        alert('Starting new scan...');
    });

    // Handle history button click
    const historyBtn = document.querySelector('.history-btn');
    historyBtn.addEventListener('click', function() {
        alert('Loading scan history...');
    });

    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});