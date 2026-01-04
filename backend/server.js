//server.js
const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const connectDB = require('./config/db');

// Load environment variables
dotenv.config();

// Connect to MongoDB
connectDB();

// Initialize Express app
const app = express();

// ========== MIDDLEWARE ==========

// Enable CORS (Cross-Origin Resource Sharing)
app.use(cors({
  origin: 'http://localhost:3000', // React app URL
  credentials: true
}));

// Body parser middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logger middleware (optional - for development)
if (process.env.NODE_ENV === 'development') {
  app.use((req, res, next) => {
    console.log(`${req.method} ${req.path}`);
    next();
  });
}

// ========== ROUTES ==========

// Test route
app.get('/', (req, res) => {
  res.json({ 
    success: true,
    message: 'Seaweed Packaging System API',
    version: '1.0.0'
  });
});

// API routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/seaweed', require('./routes/seaweed'));
app.use('/api/recipes', require('./routes/recipes'));

// ========== ERROR HANDLING ==========

// 404 handler - Route not found
app.use((req, res, next) => {
  res.status(404).json({
    success: false,
    message: 'Route not found'
  });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  
  res.status(err.status || 500).json({
    success: false,
    message: err.message || 'Server Error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// ========== START SERVER ==========

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`
  ========================================
  🚀 Server running on port ${PORT}
  📝 Environment: ${process.env.NODE_ENV}
  🌐 URL: http://localhost:${PORT}
  ========================================
  `);
});