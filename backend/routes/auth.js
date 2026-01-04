// backend\routes\auth.js
const express = require('express');
const { 
  register, 
  login, 
  getMe, 
  updateProfile, 
  changePassword, 
  deleteAccount 
} = require('../controllers/authController');
const { protect } = require('../middleware/auth');
const router = express.Router();
// Public routes
router.post('/register', register);
router.post('/login', login);
// Protected routes
router.get('/me', protect, getMe);
router.put('/update-profile', protect, updateProfile);
router.put('/change-password', protect, changePassword);
router.delete('/delete-account', protect, deleteAccount);
module.exports = router;