// backend/scripts/importEnhancedRecipes.js
require('dotenv').config();
const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');
const Recipe = require('../models/Recipe');

const importEnhancedRecipes = async () => {
  try {
    await mongoose.connect(process.env.MONGO_URI);
    console.log('✅ MongoDB Connected');

    // Load NEW format JSON
    const jsonPath = path.join(__dirname, '../models/recipes_data.json');
    const data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));

    // Clear existing
    await Recipe.deleteMany({});
    console.log('🗑️  Cleared existing recipes');

    // Map NEW format to MongoDB schema
    const recipes = data.map(r => ({
      seaweedType: r['Seaweed Type'],
      recipeName: r['Recipe Name'],
      category: r['Category'],
      prepTime: r['Prep Time'],
      servings: r['Servings'],
      dietaryRestrictions: r['Dietary Restrictions'],
      ingredients: r['Ingredients'],
      howToMake: r['How to Make'],
      calories: r['Calories'],
      protein: r['Protein'],
      carbohydrates: r['Carbohydrates'],
      fiber: r['Fiber'],
      fat: r['Fat'],
      minerals: r['Minerals']
    }));

    // Insert
    const result = await Recipe.insertMany(recipes);
    console.log(`✅ Imported ${result.length} enhanced recipes`);

    console.log('\n📋 Sample Recipe:');
    console.log(result[0]);

    process.exit(0);
  } catch (error) {
    console.error('❌ Error:', error);
    process.exit(1);
  }
};

importEnhancedRecipes();