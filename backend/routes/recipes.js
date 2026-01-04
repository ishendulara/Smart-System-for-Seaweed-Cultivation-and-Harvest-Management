// backend/routes/recipes.js
const express = require('express');
const {
  getRecipes,
  getRecipeById,
  getRecipesBySeaweedType,
  getRandomSuggestions,
  importRecipesFromCSV,
  getSeaweedTypes
} = require('../controllers/recipeController');

const {
  getFreeAIRecommendations,
  freeSuggestByIngredients,
  freeChatWithAI
} = require('../controllers/freeAIController');

const { protect, authorize } = require('../middleware/auth');

const router = express.Router();

// All routes require authentication
router.use(protect);

// Recipe routes
router.get('/', getRecipes);
router.get('/seaweed-types', getSeaweedTypes);
router.get('/suggestions/:type', getRandomSuggestions);
router.get('/seaweed/:type', getRecipesBySeaweedType);
router.get('/:id', getRecipeById);

// Import CSV (Admin only)
router.post('/import', authorize('admin'), importRecipesFromCSV);

// Free AI routes (no Python needed)
router.post('/free-ai/recommendations', getFreeAIRecommendations);
router.post('/free-ai/suggest-by-ingredients', freeSuggestByIngredients);
router.post('/free-ai/chat', freeChatWithAI);

module.exports = router;