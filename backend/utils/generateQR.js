const QRCode = require('qrcode');

/**
 * Generate QR Code as Data URL (base64)
 * @param {string} data - Data to encode in QR code
 * @returns {Promise<string>} - QR code as data URL
 */
exports.generateQRCode = async (data) => {
  try {
    // Generate QR code as data URL
    const qrCodeDataURL = await QRCode.toDataURL(data, {
      width: 300,
      margin: 2,
      color: {
        dark: '#000000',  // Black
        light: '#FFFFFF'  // White
      },
      errorCorrectionLevel: 'M'
    });
    
    return qrCodeDataURL;
  } catch (error) {
    console.error('❌ QR Code generation error:', error);
    throw new Error('Failed to generate QR code');
  }
};