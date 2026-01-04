// backend\controllers\seaweedController.js
const SeaweedRecord = require('../models/SeaweedRecord');
const User = require('../models/User');
const { generateQRCode } = require('../utils/generateQR');
const { generateLabel } = require('../utils/generateLabel');

/**
 * @desc    Create new seaweed record
 * @route   POST /api/seaweed
 * @access  Private (Farmer only)
 */
exports.createRecord = async (req, res) => {
  try {
    const { seaweedType, harvestDate, weight, processingMethod, quality, location } = req.body;

    // Validate required fields
    if (!seaweedType || !harvestDate || !weight || !processingMethod) {
      return res.status(400).json({
        success: false,
        message: 'Please provide all required fields'
      });
    }

    // Create record
    const record = await SeaweedRecord.create({
      farmer: req.user.id,
      seaweedType,
      harvestDate,
      weight,
      processingMethod,
      quality: quality || 'Grade A',
      location
    });

    // Generate QR code with record data
    const qrCodeData = {
      recordId: record.recordId,
      seaweedType: record.seaweedType,
      weight: record.weight,
      harvestDate: record.harvestDate,
      farmer: req.user.name,
      quality: record.quality
    };
    
    const qrCode = await generateQRCode(JSON.stringify(qrCodeData));
    record.qrCode = qrCode;
    await record.save();

    // Populate farmer details
    await record.populate('farmer', 'name email phone location address');

    res.status(201).json({
      success: true,
      message: 'Seaweed record created successfully',
      data: record
    });
    
  } catch (error) {
    console.error('Create record error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Server error'
    });
  }
};

/**
 * @desc    Get all records for logged-in farmer
 * @route   GET /api/seaweed/my-records
 * @access  Private (Farmer only)
 */
exports.getMyRecords = async (req, res) => {
  try {
    const records = await SeaweedRecord.find({ farmer: req.user.id })
      .sort('-createdAt')
      .populate('farmer', 'name email phone location address');

    res.status(200).json({
      success: true,
      count: records.length,
      data: records
    });
    
  } catch (error) {
    console.error('Get my records error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Server error'
    });
  }
};

/**
 * @desc    Get single record by ID
 * @route   GET /api/seaweed/:id
 * @access  Private
 */
exports.getRecord = async (req, res) => {
  try {
    const record = await SeaweedRecord.findById(req.params.id)
      .populate('farmer', 'name email phone location address');

    if (!record) {
      return res.status(404).json({
        success: false,
        message: 'Record not found'
      });
    }

    // Check authorization: farmer can only see their own records, admin can see all
    if (record.farmer._id.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to access this record'
      });
    }

    res.status(200).json({
      success: true,
      data: record
    });
    
  } catch (error) {
    console.error('Get record error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Server error'
    });
  }
};

/**
 * @desc    Update seaweed record
 * @route   PUT /api/seaweed/:id
 * @access  Private (Farmer - own records only)
 */
exports.updateRecord = async (req, res) => {
  try {
    let record = await SeaweedRecord.findById(req.params.id);

    if (!record) {
      return res.status(404).json({
        success: false,
        message: 'Record not found'
      });
    }

    // Check ownership
    if (record.farmer.toString() !== req.user.id) {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to update this record'
      });
    }

    // Don't allow updates if already approved/rejected by admin
    if (record.status !== 'pending') {
      return res.status(400).json({
        success: false,
        message: `Cannot update record that has been ${record.status} by admin`
      });
    }

    // Update record
    record = await SeaweedRecord.findByIdAndUpdate(
      req.params.id,
      req.body,
      { 
        new: true, 
        runValidators: true 
      }
    ).populate('farmer', 'name email phone location address');

    // Regenerate QR code if key fields changed
    if (req.body.seaweedType || req.body.weight || req.body.harvestDate) {
      const qrCodeData = {
        recordId: record.recordId,
        seaweedType: record.seaweedType,
        weight: record.weight,
        harvestDate: record.harvestDate,
        farmer: req.user.name,
        quality: record.quality
      };
      record.qrCode = await generateQRCode(JSON.stringify(qrCodeData));
      await record.save();
    }

    res.status(200).json({
      success: true,
      message: 'Record updated successfully',
      data: record
    });
    
  } catch (error) {
    console.error('Update record error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Server error'
    });
  }
};

/**
 * @desc    Delete seaweed record
 * @route   DELETE /api/seaweed/:id
 * @access  Private (Farmer - own records only)
 */
exports.deleteRecord = async (req, res) => {
  try {
    const record = await SeaweedRecord.findById(req.params.id);

    if (!record) {
      return res.status(404).json({
        success: false,
        message: 'Record not found'
      });
    }

    // Check ownership
    if (record.farmer.toString() !== req.user.id) {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to delete this record'
      });
    }

    await record.deleteOne();

    res.status(200).json({
      success: true,
      message: 'Record deleted successfully',
      data: {}
    });
    
  } catch (error) {
    console.error('Delete record error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Server error'
    });
  }
};

/**
 * @desc    Get all seaweed records (Admin)
 * @route   GET /api/seaweed/admin/all
 * @access  Private (Admin only)
 */
exports.getAllRecords = async (req, res) => {
  try {
    const records = await SeaweedRecord.find()
      .sort('-createdAt')
      .populate('farmer', 'name email phone location address');

    res.status(200).json({
      success: true,
      count: records.length,
      data: records
    });
    
  } catch (error) {
    console.error('Get all records error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Server error'
    });
  }
};

/**
 * @desc    Review record - Approve or Reject (Admin)
 * @route   PUT /api/seaweed/admin/:id/review
 * @access  Private (Admin only)
 */
exports.reviewRecord = async (req, res) => {
  try {
    const { status, adminNotes } = req.body;

    // Validate status
    if (!status || !['approved', 'rejected'].includes(status)) {
      return res.status(400).json({
        success: false,
        message: 'Status must be either "approved" or "rejected"'
      });
    }

    const record = await SeaweedRecord.findByIdAndUpdate(
      req.params.id,
      { 
        status, 
        adminNotes: adminNotes || '' 
      },
      { 
        new: true, 
        runValidators: true 
      }
    ).populate('farmer', 'name email phone location address');

    if (!record) {
      return res.status(404).json({
        success: false,
        message: 'Record not found'
      });
    }

    res.status(200).json({
      success: true,
      message: `Record ${status} successfully`,
      data: record
    });
    
  } catch (error) {
    console.error('Review record error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Server error'
    });
  }
};

/**
 * @desc    Generate and download product label PDF
 * @route   GET /api/seaweed/:id/label
 * @access  Private
 */
exports.downloadLabel = async (req, res) => {
  try {
    const record = await SeaweedRecord.findById(req.params.id)
      .populate('farmer', 'name email phone location address');

    if (!record) {
      return res.status(404).json({
        success: false,
        message: 'Record not found'
      });
    }

    // Check authorization
    if (record.farmer._id.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to generate label for this record'
      });
    }

    // Generate PDF label
    const pdfBuffer = await generateLabel(record, record.farmer);

    // Set response headers for PDF download
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=label-${record.recordId}.pdf`);
    res.setHeader('Content-Length', pdfBuffer.length);

    // Send PDF
    res.send(pdfBuffer);
    
  } catch (error) {
    console.error('Download label error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to generate label'
    });
  }
};

/**
 * @desc    Generate packing checklist for approved record (Admin)
 * @route   GET /api/seaweed/admin/:id/packing-checklist
 * @access  Private (Admin only)
 */
exports.generatePackingChecklist = async (req, res) => {
  try {
    const record = await SeaweedRecord.findById(req.params.id)
      .populate('farmer', 'name email phone location address');

    if (!record) {
      return res.status(404).json({
        success: false,
        message: 'Record not found'
      });
    }

    if (record.status !== 'approved') {
      return res.status(400).json({
        success: false,
        message: 'Can only generate packing checklist for approved records'
      });
    }

    // Generate packing checklist data
    const checklist = {
      recordId: record.recordId,
      farmerName: record.farmer.name,
      seaweedType: record.seaweedType,
      weight: record.weight,
      quality: record.quality,
      processingMethod: record.processingMethod,
      harvestDate: record.harvestDate,
      tasks: [
        {
          id: 1,
          task: 'Verify seaweed quality matches grade',
          completed: false
        },
        {
          id: 2,
          task: 'Check weight accuracy',
          completed: false
        },
        {
          id: 3,
          task: 'Inspect for contamination',
          completed: false
        },
        {
          id: 4,
          task: 'Package according to processing method',
          completed: false
        },
        {
          id: 5,
          task: 'Attach product label',
          completed: false
        },
        {
          id: 6,
          task: 'Attach QR code',
          completed: false
        },
        {
          id: 7,
          task: 'Seal package properly',
          completed: false
        },
        {
          id: 8,
          task: 'Store in appropriate conditions',
          completed: false
        }
      ],
      generatedDate: new Date(),
      generatedBy: req.user.name
    };

    res.status(200).json({
      success: true,
      message: 'Packing checklist generated successfully',
      data: checklist
    });
    
  } catch (error) {
    console.error('Generate packing checklist error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Server error'
    });
  }
};

/**
 * @desc    Generate delivery summary
 * @route   GET /api/seaweed/:id/delivery-summary
 * @access  Private
 */
exports.generateDeliverySummary = async (req, res) => {
  try {
    const record = await SeaweedRecord.findById(req.params.id)
      .populate('farmer', 'name email phone location address');

    if (!record) {
      return res.status(404).json({
        success: false,
        message: 'Record not found'
      });
    }

    // Check authorization
    if (record.farmer._id.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to access this delivery summary'
      });
    }

    // Generate delivery summary
    const deliverySummary = {
      recordId: record.recordId,
      productDetails: {
        type: record.seaweedType,
        weight: `${record.weight} kg`,
        quality: record.quality,
        processingMethod: record.processingMethod,
        harvestDate: new Date(record.harvestDate).toLocaleDateString()
      },
      farmerDetails: {
        name: record.farmer.name,
        phone: record.farmer.phone || 'N/A',
        email: record.farmer.email,
        address: record.farmer.address || 'N/A'
      },
      locationDetails: {
        latitude: record.location?.latitude || record.farmer.location?.latitude,
        longitude: record.location?.longitude || record.farmer.location?.longitude,
        address: record.location?.address || record.farmer.location?.address || 'N/A'
      },
      status: record.status,
      adminNotes: record.adminNotes || 'No notes',
      generatedDate: new Date()
    };

    res.status(200).json({
      success: true,
      message: 'Delivery summary generated successfully',
      data: deliverySummary
    });
    
  } catch (error) {
    console.error('Generate delivery summary error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Server error'
    });
  }
};