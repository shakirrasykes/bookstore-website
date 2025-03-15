document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // Simulate server-side login validation
    if (username === 'admin' && password === 'password') {
        localStorage.setItem('isLoggedIn', 'true'); // Set isLoggedIn in localStorage
        window.location.href = 'admin-home.html'; // Redirect to admin home page
    } else {
        document.getElementById('error-message').textContent = 'Invalid username or password';
    }
});
