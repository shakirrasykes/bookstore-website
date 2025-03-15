const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const axios = require('axios');
const { generateSalesReport } = require('./salesReports');
const path = require('path');

const app = express();
const port = 3000;

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json()); // Add this line to parse JSON bodies
app.use(express.static(path.join(__dirname)));

// MongoDB connection
mongoose.connect('mongodb://localhost:27017/bookstore', { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => {
        console.log('Connected to MongoDB');
        // Insert a fake user
        const User = mongoose.model('User', userSchema);
        User.findOne({ username: 'fakeuser' }).then(user => {
            if (!user) {
                const fakeUser = new User({
                    username: 'fakeuser',
                    password: 'fakepassword',
                    role: 'user'
                });
                fakeUser.save().then(() => console.log('Fake user created'));
            }
        });
    })
    .catch(err => console.error('Could not connect to MongoDB', err));

// User schema and model
const userSchema = new mongoose.Schema({
    username: String,
    password: String,
    role: String // Add role field to differentiate between admin and user
});
const User = mongoose.model('User', userSchema);

// Book schema and model
const bookSchema = new mongoose.Schema({
    title: String,
    author: String,
    genre: String,
    cover: String
});
const Book = mongoose.model('Book', bookSchema);

// Routes
app.post('/login', async (req, res) => {
    try {
        const { username, password } = req.body;
        const user = await User.findOne({ username, password });
        if (user) {
            res.send('Login successful');
        } else {
            res.status(401).send('Invalid username or password');
        }
    } catch (error) {
        console.error('Error during login:', error);
        res.status(500).send('Internal server error');
    }
});

app.post('/admin-login', async (req, res) => {
    try {
        const { username, password } = req.body;
        const admin = await User.findOne({ username, password, role: 'admin' });
        if (admin) {
            res.send('Admin login successful');
        } else {
            res.status(401).send('Invalid admin username or password');
        }
    } catch (error) {
        console.error('Error during admin login:', error);
        res.status(500).send('Internal server error');
    }
});

// Route for user signup
app.post('/signup', async (req, res) => {
    try {
        const { username, password } = req.body;
        const newUser = new User({ username, password, role: 'user' });
        await newUser.save();
        res.send('User signed up successfully');
    } catch (error) {
        console.error('Error during signup:', error);
        res.status(500).send('Internal server error');
    }
});

// Route to check if user is admin
app.get('/is-admin', async (req, res) => {
    try {
        const { username } = req.query;
        const user = await User.findOne({ username, role: 'admin' });
        if (user) {
            res.json({ isAdmin: true });
        } else {
            res.json({ isAdmin: false });
        }
    } catch (error) {
        console.error('Error checking admin status:', error);
        res.status(500).send('Internal server error');
    }
});

// Route to get inventory from external API
app.get('/inventory', async (req, res) => {
    try {
        const response = await axios.get('https://bookstore-api-vj13.onrender.com/inventory');
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching inventory:', error);
        res.status(500).send('Error fetching inventory');
    }
});

// Route to generate sales report
app.get('/sales-report/:period', async (req, res) => {
    try {
        const period = req.params.period;
        const totalSales = await generateSalesReport(period);
        res.json({ period, totalSales });
    } catch (error) {
        console.error('Error generating sales report:', error);
        res.status(500).send('Error generating sales report');
    }
});

// Route to add a book to the server
app.post('/add-book', async (req, res) => {
    try {
        const { title, author, genre, cover } = req.body;
        const newBook = new Book({ title, author, genre, cover });
        await newBook.save();
        res.send('Book added successfully');
    } catch (error) {
        console.error('Error adding book:', error);
        res.status(500).send('Error adding book');
    }
});

// Route to update user password
app.post('/update-password', async (req, res) => {
    try {
        const { username, oldPassword, newPassword } = req.body;
        const user = await User.findOne({ username, password: oldPassword });
        if (user) {
            user.password = newPassword;
            await user.save();
            res.send('Password updated successfully');
        } else {
            res.status(401).send('Invalid username or old password');
        }
    } catch (error) {
        console.error('Error updating password:', error);
        res.status(500).send('Internal server error');
    }
});

// Route to serve OrderingReport.html
app.get('/ordering-report', (req, res) => {
    res.sendFile(__dirname + '/OrderingReport.html');
});

// Route to serve manage-users.html
app.get('/manage-users', (req, res) => {
    res.sendFile(__dirname + '/manage-users.html');
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}/`);
});
