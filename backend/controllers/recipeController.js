// backend\controllers\recipeController.js
const Recipe = require('../models/Recipe');

// GET all recipes
exports.getRecipes = async (req, res) => {
  try {
    const recipes = await Recipe.find().sort({ createdAt: -1 });
    res.status(200).json({ success: true, count: recipes.length, data: recipes });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// GET recipe by ID
exports.getRecipeById = async (req, res) => {
  try {
    const recipe = await Recipe.findById(req.params.id);
    if (!recipe) {
      return res.status(404).json({ success: false, message: 'Recipe not found' });
    }
    res.status(200).json({ success: true, data: recipe });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// GET recipes by seaweed type
exports.getRecipesBySeaweedType = async (req, res) => {
  try {
    const recipes = await Recipe.find({ seaweedType: req.params.type });
    res.status(200).json({ success: true, count: recipes.length, data: recipes });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// GET random recipe suggestions
exports.getRandomSuggestions = async (req, res) => {
  try {
    const limit = Number(req.query.limit) || 5;
    const recipes = await Recipe.aggregate([{ $sample: { size: limit } }]);
    res.status(200).json({ success: true, data: recipes });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// IMPORT recipes from CSV (Admin)
exports.importRecipesFromCSV = async (req, res) => {
  res.status(200).json({
    success: true,
    message: 'CSV import handled via script'
  });
};

// GET distinct seaweed types
exports.getSeaweedTypes = async (req, res) => {
  try {
    const types = await Recipe.distinct('seaweedType');
    res.status(200).json({ success: true, data: types });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};
