// backend/models/SeaweedRecord.js
const mongoose = require('mongoose');

const seaweedRecordSchema = new mongoose.Schema({
  farmer: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  seaweedType: {
    type: String,
    required: true,
    enum: ['Gracilaria', 'Sargassum', 'Ulva', 'Caulerpa', 'Gelidium', 'Other']
  },
  harvestDate: {
    type: Date,
    required: true
  },
  weight: {
    type: Number,
    required: true,
    min: 0
  },
  processingMethod: {
    type: String,
    enum: ['Fresh', 'Dried', 'Semi-dried', 'Frozen'],
    required: true
  },
  quality: {
    type: String,
    enum: ['Premium', 'Grade A', 'Grade B', 'Grade C'],
    default: 'Grade A'
  },
  location: {
    latitude: Number,
    longitude: Number,
    address: String
  },
  status: {
    type: String,
    enum: ['pending', 'approved', 'rejected'],
    default: 'pending'
  },
  adminNotes: String,
  qrCode: String,
  recordId: {
    type: String,
    unique: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

/**
 * ✅ FIXED pre-save middleware
 * ❌ no next()
 * ✅ async only
 */
seaweedRecordSchema.pre('save', async function () {
  if (!this.recordId) {
    const timestamp = Date.now();
    const randomStr = Math.random()
      .toString(36)
      .substring(2, 11)
      .toUpperCase();

    this.recordId = `SW-${timestamp}-${randomStr}`;
  }

  this.updatedAt = Date.now();
});

module.exports = mongoose.model('SeaweedRecord', seaweedRecordSchema);
