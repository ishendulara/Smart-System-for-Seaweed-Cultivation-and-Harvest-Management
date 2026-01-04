// backend/models/Recipe.js
const mongoose = require('mongoose');

const recipeSchema = new mongoose.Schema({
  seaweedType: {
    type: String,
    required: true,
    enum: ['Kappaphycus Alvarezii', 'Gracilaria Edulis'],
    index: true
  },
  recipeName: {
    type: String,
    required: true,
    trim: true
  },
  category: {
    type: String,
    enum: ['Breakfast', 'Lunch', 'Dinner', 'Snack', 'Dessert', 'Beverage', 'Salad', 'Main Dish', 'Side Dish', 'Soup', 'Appetizer', 'Supplement/ Powder', 'Side Dish/ Appetizer', 'Healthy Meal', 'Snack, Appetizer'],
    default: 'Lunch',
    index: true
  },
  prepTime: {
    type: String,
    default: '30 mins'
  },
  servings: {
    type: String,
    default: '4'
  },
  dietaryRestrictions: {
    type: String,
    default: 'None'
  },
  ingredients: {
    type: String,
    required: true
  },
  howToMake: {
    type: String,
    required: true
  },
  // Enhanced nutrition fields
  calories: {
    type: String,
    default: '0'
  },
  protein: {
    type: String,
    default: '0g'
  },
  carbohydrates: {
    type: String,
    default: '0g'
  },
  fiber: {
    type: String,
    default: '0g'
  },
  fat: {
    type: String,
    default: '0g'
  },
  minerals: {
    type: String,
    default: ''
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// Text search index
recipeSchema.index({ recipeName: 'text', ingredients: 'text' });

module.exports = mongoose.model('Recipe', recipeSchema);