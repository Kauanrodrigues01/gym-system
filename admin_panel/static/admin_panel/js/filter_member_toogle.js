document.addEventListener('DOMContentLoaded', () => {
    const filterToggleButton = document.querySelector('.btn-filter-toggle');
    const filterSection = document.getElementById('filter-section');

    filterToggleButton.addEventListener('click', () => {
        filterSection.classList.toggle('visible');
    });
});  