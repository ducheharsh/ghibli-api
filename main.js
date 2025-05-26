// Main JavaScript for Ghibli Landscapes Website

document.addEventListener('DOMContentLoaded', function() {
    // Elements for random image section
    const randomImageElement = document.getElementById('random-image');
    const randomImageInfo = document.getElementById('random-image-info');
    const getRandomButton = document.getElementById('get-random');

    // Elements for search section
    const searchQueryInput = document.getElementById('search-query');
    const searchButton = document.getElementById('search-button');
    const searchImage = document.getElementById('search-image');
    const searchImageInfo = document.getElementById('search-image-info');

    // Elements for film section
    const filmSelect = document.getElementById('film-select');
    const getFilmImageButton = document.getElementById('get-film-image');
    const filmImage = document.getElementById('film-image');
    const filmImageInfo = document.getElementById('film-image-info');

    // Function to get a random image
    function getRandomImage() {
        fetch('/api/random')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                randomImageElement.src = data.url;
                randomImageInfo.textContent = `Film: ${data.film_code} | ID: ${data.id}`;
            })
            .catch(error => {
                console.error('Error fetching random image:', error);
                randomImageInfo.textContent = 'Error loading image. Please try again.';
            });
    }

    // Function to get an image by query
    function getImageByQuery(query) {
        if (!query.trim()) {
            searchImageInfo.textContent = 'Please enter a search query';
            return;
        }

        fetch(`/api/image?q=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                searchImage.src = data.url;
                searchImageInfo.textContent = `Query: "${query}" | Film: ${data.film_code} | ID: ${data.id}`;
            })
            .catch(error => {
                console.error('Error fetching image by query:', error);
                searchImageInfo.textContent = 'Error loading image. Please try again.';
            });
    }

    // Function to get an image by film
    function getImageByFilm(filmCode) {
        if (!filmCode) {
            filmImageInfo.textContent = 'Please select a film';
            return;
        }

        fetch(`/api/film/${filmCode}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                filmImage.src = data.url;
                filmImageInfo.textContent = `Film: ${data.film_code} | ID: ${data.id}`;
            })
            .catch(error => {
                console.error('Error fetching image by film:', error);
                filmImageInfo.textContent = 'Error loading image. Please try again.';
            });
    }

    // Event listeners
    if (getRandomButton) {
        getRandomButton.addEventListener('click', getRandomImage);
    }

    if (searchButton) {
        searchButton.addEventListener('click', function() {
            getImageByQuery(searchQueryInput.value);
        });

        // Also trigger search on Enter key
        searchQueryInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                getImageByQuery(searchQueryInput.value);
            }
        });
    }

    if (getFilmImageButton) {
        getFilmImageButton.addEventListener('click', function() {
            getImageByFilm(filmSelect.value);
        });

        // Also trigger on select change
        filmSelect.addEventListener('change', function() {
            if (filmSelect.value) {
                getImageByFilm(filmSelect.value);
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Offset for header
                    behavior: 'smooth'
                });
            }
        });
    });
});
