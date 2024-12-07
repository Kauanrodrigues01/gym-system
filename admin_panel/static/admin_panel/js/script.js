document.addEventListener("DOMContentLoaded", function () {
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'scale(1.05)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'scale(1)';
        });
    });
});



document.addEventListener("DOMContentLoaded", function () {
    const addStudentBtn = document.getElementById('add-student-btn');
    const modalOverlay = document.getElementById('modal-overlay');
    const modalCloseBtn = document.getElementById('modal-close-btn');

    addStudentBtn.addEventListener('click', function() {
        modalOverlay.style.display = 'flex';
    });

    modalCloseBtn.addEventListener('click', function() {
        modalOverlay.style.display = 'none';
    });

    const form = document.getElementById('add-student-form');
});
 