document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const bookForm = document.getElementById('book-form');
    const bookList = document.querySelector('.book-list');
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const logoutButton = document.getElementById('logout');

    // Handle login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            const users = {
                'admin': 'admin123',
                'user': 'user123'
            };

            if (users[username] && users[username] === password) {
                alert('Login successful!');
                sessionStorage.setItem('role', username);
                window.location.href = 'search.html';
            } else {
                alert('Invalid username or password');
            }
        });
    }

    // Fetch and display books
    function fetchBooks() {
        fetch('https://bookstore-api-vj13.onrender.com/inventory')
            .then(response => response.json())
            .then(data => {
                if (bookList) {
                    bookList.innerHTML = '';
                    data.forEach(book => {
                        const bookItem = document.createElement('div');
                        bookItem.classList.add('book-item');
                        bookItem.innerHTML = `
                            <img src="${book.cover}" alt="Book Cover">
                            <p>${book.title}</p>
                            <p><strong>Author:</strong> ${book.author}</p>
                            <p><strong>Genre:</strong> ${book.genre}</p>
                        `;
                        bookList.appendChild(bookItem);
                    });
                }
            })
            .catch(error => console.error('Error fetching books:', error));
    }

    // Add a new book
    if (bookForm) {
        bookForm.addEventListener('submit', function(event) {
            event.preventDefault();

            const formData = new FormData(bookForm);
            const data = {
                title: formData.get('title'),
                author: formData.get('author'),
                genre: formData.get('genre'),
                cover: formData.get('cover')
            };

            fetch('http://localhost:3000/api/books', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                alert('Book added successfully!');
                fetchBooks();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again later.');
            });
        });
    }

    // Search books
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = searchInput.value.toLowerCase();
            fetch(`https://bookstore-api-vj13.onrender.com/inventory?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    if (searchResults) {
                        searchResults.innerHTML = '';
                        data.forEach(book => {
                            const resultItem = document.createElement('div');
                            resultItem.classList.add('result-item');
                            resultItem.innerHTML = `
                                <p>${book.title} by ${book.author} (${book.genre})</p>
                            `;
                            searchResults.appendChild(resultItem);
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred. Please try again later.');
                });
        });
    }

    // Initial fetch of books
    fetchBooks();

    // Handle logout
    if (logoutButton) {
        logoutButton.addEventListener('click', function() {
            sessionStorage.removeItem('role');
            window.location.href = 'login.html';
        });
    }

    // Fetch books from new API
    fetch('https://bookstore-api-vj13.onrender.com/inventory')
        .then(response => response.json())
        .then(data => {
            const event = new CustomEvent('booksDataLoaded', { detail: data });
            document.dispatchEvent(event);
        })
        .catch(error => console.error('Error fetching books:', error));
});
