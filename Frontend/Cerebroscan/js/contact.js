document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');

    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Get form values
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            query: document.getElementById('query').value
        };

        // Here you would typically send the data to your server
        // For now, we'll just show a success message
        alert('Thank you for your message! We will get back to you soon.');
        contactForm.reset();
    });
});