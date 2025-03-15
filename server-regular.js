const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const axios = require('axios');

const app = express();
const port = 3001; // Use a different port for the regular login server

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// MongoDB connection
mongoose.connect('mongodb://localhost:27017/bookstore', { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.error('Could not connect to MongoDB', err));

// User schema and model
const userSchema = new mongoose.Schema({
    username: String,
    password: String,
    role: String
});
const User = mongoose.model('User', userSchema);

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

// Start the server
app.listen(port, () => {
    console.log(`Regular login server is running on http://localhost:${port}`);
});
