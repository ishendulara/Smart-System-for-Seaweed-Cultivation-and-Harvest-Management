// backend\routes\seaweed.js
const express = require('express');
const {
  createRecord,
  getMyRecords,
  getRecord,
  updateRecord,
  deleteRecord,
  getAllRecords,
  reviewRecord,
  downloadLabel,
  generatePackingChecklist,
  generateDeliverySummary
} = require('../controllers/seaweedController');
const { protect, authorize } = require('../middleware/auth');

const router = express.Router();

// ========== FARMER ROUTES ==========

// Create new record (Farmer only)
router.post('/', protect, authorize('farmer'), createRecord);

// Get all records for logged-in farmer
router.get('/my-records', protect, authorize('farmer'), getMyRecords);

// Get single record (Farmer can see own, Admin can see all)
router.get('/:id', protect, getRecord);

// Update record (Farmer - own records only, only if pending)
router.put('/:id', protect, authorize('farmer'), updateRecord);

// Delete record (Farmer - own records only)
router.delete('/:id', protect, authorize('farmer'), deleteRecord);

// Download label PDF
router.get('/:id/label', protect, downloadLabel);

// Generate delivery summary
router.get('/:id/delivery-summary', protect, generateDeliverySummary);

// ========== ADMIN ROUTES ==========

// Get all records (Admin only)
router.get('/admin/all', protect, authorize('admin'), getAllRecords);

// Review record - Approve/Reject (Admin only)
router.put('/admin/:id/review', protect, authorize('admin'), reviewRecord);

// Generate packing checklist (Admin only)
router.get('/admin/:id/packing-checklist', protect, authorize('admin'), generatePackingChecklist);

module.exports = router;