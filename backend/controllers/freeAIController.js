// backend/controllers/freeAIController.js
// Complete JavaScript AI Controller (No Python Required)
// 100% Working - Production Ready

const Recipe = require('../models/Recipe');

/**
 * @desc    Get AI-powered recipe recommendations
 * @route   POST /api/recipes/free-ai/recommendations
 * @access  Private
 */
exports.getFreeAIRecommendations = async (req, res) => {
  try {
    console.log('🎯 AI Recommendations (JavaScript):', req.body);
    
    const { seaweedType, dietaryRestrictions, healthGoals, preferredMealType, skillLevel } = req.body;
    
    // Validate seaweed type
    if (!seaweedType) {
      return res.status(400).json({
        success: false,
        message: 'Please select a seaweed type',
        data: []
      });
    }
    
    // Build MongoDB query
    let query = { seaweedType };
    
    // Filter by meal type/category
    if (preferredMealType && preferredMealType !== 'any') {
      query.category = preferredMealType;
    }
    
    console.log('📊 MongoDB Query (Before Dietary):', JSON.stringify(query, null, 2));
    
    // Get recipes from database (without dietary filter first)
    let recipes = await Recipe.find(query).limit(50);
    
    console.log(`📦 Found ${recipes.length} recipes`);
    
    // NOW filter by dietary restrictions in JavaScript (more accurate)
    if (dietaryRestrictions && dietaryRestrictions.length > 0) {
      console.log('🔍 Filtering by dietary restrictions:', dietaryRestrictions);
      
      recipes = recipes.filter(recipe => {
        // Split dietaryRestrictions by comma
        const dietaryArray = recipe.dietaryRestrictions
          .split(',')
          .map(d => d.trim().toLowerCase());

        // Check if all user-selected restrictions are present
        return dietaryRestrictions.every(restriction =>
          dietaryArray.includes(restriction.toLowerCase())
        );
      });
      
      console.log(`✅ After dietary filter: ${recipes.length} recipes`);
    }
    
    // If no recipes found
    if (recipes.length === 0) {
      return res.status(200).json({
        success: true,
        data: [],
        message: 'No recipes found. Try different filters!'
      });
    }
    
    // Score and rank recipes
    recipes = recipes.map((recipe, index) => {
      let score = 90 - (index * 1.5); // Base score
      
      // Health goals bonus
      if (healthGoals && healthGoals.length > 0) {
        // Weight Loss
        if (healthGoals.includes('Weight Loss')) {
          const calories = parseInt(recipe.calories.replace(/[^\d]/g, '')) || 999;
          if (calories < 200) score += 15;
          else if (calories < 300) score += 10;
          else if (calories < 400) score += 5;
        }
        
        // Muscle Gain
        if (healthGoals.includes('Muscle Gain')) {
          const protein = parseInt(recipe.protein.replace(/[^\d]/g, '')) || 0;
          if (protein > 15) score += 15;
          else if (protein > 10) score += 10;
          else if (protein > 5) score += 5;
        }
        
        // Heart Health
        if (healthGoals.includes('Heart Health')) {
          const minerals = recipe.minerals.toLowerCase();
          if (minerals.includes('omega')) score += 15;
          if (minerals.includes('potassium')) score += 10;
          if (recipe.dietaryRestrictions.toLowerCase().includes('low fat')) score += 5;
        }
        
        // Energy Boost
        if (healthGoals.includes('Energy Boost')) {
          const carbs = parseInt(recipe.carbohydrates.replace(/[^\d]/g, '')) || 0;
          if (carbs > 30) score += 10;
          else if (carbs > 20) score += 5;
        }
      }
      
      // Skill level bonus
      const prepTime = parseInt(recipe.prepTime.replace(/[^\d]/g, '')) || 999;
      if (skillLevel === 'beginner' && prepTime <= 20) score += 5;
      if (skillLevel === 'intermediate' && prepTime <= 40) score += 3;
      
      // Extract health benefits
      const healthBenefits = [];
      const proteinNum = parseInt(recipe.protein.replace(/[^\d]/g, '')) || 0;
      const fiberNum = parseInt(recipe.fiber.replace(/[^\d]/g, '')) || 0;
      const calorieNum = parseInt(recipe.calories.replace(/[^\d]/g, '')) || 0;
      const minerals = recipe.minerals.toLowerCase();
      
      if (proteinNum > 10) healthBenefits.push('High Protein');
      if (fiberNum > 5) healthBenefits.push('Rich in Fiber');
      if (calorieNum < 200) healthBenefits.push('Low Calorie');
      if (minerals.includes('vitamin')) healthBenefits.push('Vitamin Rich');
      if (minerals.includes('calcium') || minerals.includes('iron')) {
        healthBenefits.push('Mineral Rich');
      }
      if (minerals.includes('omega')) healthBenefits.push('Heart Healthy');
      
      // Build recommendation reason
      const reasons = [];
      reasons.push(`Perfect ${recipe.category}`);
      
      if (dietaryRestrictions && dietaryRestrictions.length > 0) {
        reasons.push(dietaryRestrictions.join(', ') + ' friendly');
      }
      
      if (prepTime <= 20) {
        reasons.push('Quick to prepare');
      } else if (prepTime <= 30) {
        reasons.push('Easy to make');
      }
      
      // Matching preferences
      const matchingPreferences = ['Seaweed Type'];
      if (preferredMealType !== 'any') matchingPreferences.push('Category');
      if (dietaryRestrictions.length > 0) matchingPreferences.push('Diet');
      if (healthGoals.length > 0) matchingPreferences.push('Health Goals');
      
      return {
        recipeId: recipe._id,
        recipeName: recipe.recipeName,
        seaweedType: recipe.seaweedType,
        category: recipe.category,
        prepTime: recipe.prepTime,
        servings: recipe.servings,
        dietaryRestrictions: recipe.dietaryRestrictions,
        ingredients: recipe.ingredients,
        howToMake: recipe.howToMake,
        calories: recipe.calories,
        protein: recipe.protein,
        carbohydrates: recipe.carbohydrates,
        fiber: recipe.fiber,
        fat: recipe.fat,
        minerals: recipe.minerals,
        score: Math.min(Math.round(score), 98),
        reason: reasons.join(' • '),
        healthBenefits: healthBenefits.slice(0, 4),
        matchingPreferences: matchingPreferences.slice(0, 3)
      };
    });
    
    // Sort by score
    recipes.sort((a, b) => b.score - a.score);
    
    // Return top 5
    const recommendations = recipes.slice(0, 5);
    
    console.log(`✅ Returning ${recommendations.length} recommendations`);
    console.log('Top scores:', recommendations.map(r => `${r.recipeName}: ${r.score}%`).join(', '));
    
    res.status(200).json({
      success: true,
      data: recommendations,
      message: `Found ${recommendations.length} personalized recommendations`
    });
    
  } catch (error) {
    console.error('❌ Error in recommendations:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to generate recommendations',
      data: []
    });
  }
};

/**
 * @desc    Suggest recipes by available ingredients
 * @route   POST /api/recipes/free-ai/suggest-by-ingredients
 * @access  Private
 */
exports.freeSuggestByIngredients = async (req, res) => {
  try {
    console.log('🥘 Ingredient Suggestions:', req.body);
    
    const { ingredients, seaweedType, category } = req.body;
    
    // Validate ingredients
    if (!ingredients || ingredients.length === 0) {
      return res.status(400).json({
        success: false,
        message: 'Please add at least one ingredient',
        suggestions: []
      });
    }
    
    // Build query
    let query = {};
    if (seaweedType) query.seaweedType = seaweedType;
    if (category) query.category = category;
    
    console.log('📊 Query:', JSON.stringify(query, null, 2));
    console.log('🔍 Searching for ingredients:', ingredients);
    
    // Get recipes
    const recipes = await Recipe.find(query);
    
    console.log(`📦 Found ${recipes.length} recipes to match`);
    
    // Match ingredients
    const suggestions = [];
    
    for (const recipe of recipes) {
      const recipeIngredients = recipe.ingredients.toLowerCase();
      
      // Count matches
      let matchCount = 0;
      const matchedIngredients = [];
      
      for (const ing of ingredients) {
        if (recipeIngredients.includes(ing.toLowerCase())) {
          matchCount++;
          matchedIngredients.push(ing);
        }
      }
      
      // Skip if no matches
      if (matchCount === 0) continue;
      
      // Calculate match percentage
      const matchPercentage = Math.round((matchCount / ingredients.length) * 100);
      
      // Find missing ingredients
      const allIngredients = recipe.ingredients
        .split(',')
        .map(i => i.trim());
      
      const missing = [];
      for (const ing of allIngredients) {
        if (missing.length >= 3) break;
        
        const found = ingredients.some(userIng => 
          ing.toLowerCase().includes(userIng.toLowerCase())
        );
        
        if (!found) {
          missing.push(ing);
        }
      }
      
      suggestions.push({
        recipeId: recipe._id,
        recipeName: recipe.recipeName,
        seaweedType: recipe.seaweedType,
        category: recipe.category,
        prepTime: recipe.prepTime,
        calories: recipe.calories,
        dietaryRestrictions: recipe.dietaryRestrictions,
        matchCount,
        matchPercentage,
        missingIngredients: missing,
        matchedIngredients,
        reason: `${matchCount} of your ingredient${matchCount !== 1 ? 's' : ''} match${matchCount === 1 ? 'es' : ''}`,
        recipe: {
          ingredients: recipe.ingredients,
          howToMake: recipe.howToMake,
          protein: recipe.protein,
          fiber: recipe.fiber,
          minerals: recipe.minerals,
          servings: recipe.servings,
          carbohydrates: recipe.carbohydrates,
          fat: recipe.fat
        }
      });
    }
    
    console.log(`🔍 Found ${suggestions.length} matching recipes`);
    
    // Sort by match count then percentage
    suggestions.sort((a, b) => {
      if (b.matchCount !== a.matchCount) {
        return b.matchCount - a.matchCount;
      }
      return b.matchPercentage - a.matchPercentage;
    });
    
    // Return top 5
    const topSuggestions = suggestions.slice(0, 5);
    
    console.log(`✅ Returning ${topSuggestions.length} suggestions`);
    console.log('Top matches:', topSuggestions.map(s => 
      `${s.recipeName}: ${s.matchCount}/${ingredients.length} (${s.matchPercentage}%)`
    ));
    
    res.status(200).json({
      success: true,
      suggestions: topSuggestions,
      count: topSuggestions.length,
      searchedIngredients: ingredients,
      filters: { seaweedType, category }
    });
    
  } catch (error) {
    console.error('❌ Error in ingredient suggestions:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to suggest recipes',
      suggestions: []
    });
  }
};

/**
 * @desc    Chat with AI about recipes (Enhanced)
 * @route   POST /api/recipes/free-ai/chat
 * @access  Private
 */
exports.freeChatWithAI = async (req, res) => {
  try {
    console.log('💬 AI Chat:', req.body);
    
    const { message } = req.body;
    
    // Validate message
    if (!message || !message.trim()) {
      return res.status(400).json({
        success: false,
        response: 'Please ask me something! 😊',
        message: 'Message is required'
      });
    }
    
    const msg = message.toLowerCase().trim();
    let response = '';
    
    // ========== GREETING QUERIES ==========
    if (msg === 'hi' || msg === 'hello' || msg === 'hey') {
      response = `Hello! 👋 I'm your seaweed recipe assistant!\n\n`;
      response += `I can help you with:\n`;
      response += `• Finding recipes by meal type (breakfast, lunch, dinner)\n`;
      response += `• Dietary preferences (vegetarian, vegan)\n`;
      response += `• Quick and easy recipes\n`;
      response += `• Nutritional information\n\n`;
      response += `What would you like to know?`;
    }
    
    // ========== BREAKFAST QUERIES ==========
    else if (msg.includes('breakfast')) {
      const recipes = await Recipe.find({ category: 'Breakfast' }).limit(5);
      
      if (recipes.length > 0) {
        response = `🍳 **Breakfast Recipes** (${recipes.length} found)\n\n`;
        recipes.forEach((r, i) => {
          response += `**${i + 1}. ${r.recipeName}**\n`;
          response += `   🌊 ${r.seaweedType}\n`;
          response += `   ⏱️ ${r.prepTime} | 🍽️ ${r.servings} servings\n`;
          response += `   🔥 ${r.calories} | ${r.dietaryRestrictions}\n\n`;
        });
        response += `💡 *Click on Smart Recommendations to get personalized breakfast suggestions!*`;
      } else {
        response = `😔 I don't have any breakfast recipes at the moment.\n\n`;
        response += `Try asking about:\n`;
        response += `• Lunch recipes\n`;
        response += `• Dinner options\n`;
        response += `• Snacks\n`;
      }
    }
    
    // ========== LUNCH QUERIES ==========
    else if (msg.includes('lunch')) {
      const recipes = await Recipe.find({ category: 'Lunch' }).limit(5);
      
      if (recipes.length > 0) {
        response = `🍱 **Lunch Recipes** (${recipes.length} found)\n\n`;
        recipes.forEach((r, i) => {
          response += `**${i + 1}. ${r.recipeName}**\n`;
          response += `   🌊 ${r.seaweedType}\n`;
          response += `   ⏱️ ${r.prepTime} | 🍽️ ${r.servings} servings\n`;
          response += `   🔥 ${r.calories} | ${r.dietaryRestrictions}\n\n`;
        });
        response += `💡 *Use Smart Recommendations for personalized lunch ideas!*`;
      } else {
        response = `😔 No lunch recipes available right now. Try asking about dinner or snacks!`;
      }
    }
    
    // ========== DINNER QUERIES ==========
    else if (msg.includes('dinner')) {
      const recipes = await Recipe.find({ category: 'Dinner' }).limit(5);
      
      if (recipes.length > 0) {
        response = `🍽️ **Dinner Recipes** (${recipes.length} found)\n\n`;
        recipes.forEach((r, i) => {
          response += `**${i + 1}. ${r.recipeName}**\n`;
          response += `   🌊 ${r.seaweedType}\n`;
          response += `   ⏱️ ${r.prepTime} | 🍽️ ${r.servings} servings\n`;
          response += `   🔥 ${r.calories} | ${r.dietaryRestrictions}\n\n`;
        });
        response += `💡 *Get personalized dinner recommendations using Smart Recommendations tab!*`;
      } else {
        response = `😔 No dinner recipes found. Try other meal categories!`;
      }
    }
    
    // ========== SNACK QUERIES ==========
    else if (msg.includes('snack')) {
      const recipes = await Recipe.find({ category: 'Snack' }).limit(5);
      
      if (recipes.length > 0) {
        response = `😋 **Snack Recipes** (${recipes.length} found)\n\n`;
        recipes.forEach((r, i) => {
          response += `**${i + 1}. ${r.recipeName}**\n`;
          response += `   🌊 ${r.seaweedType}\n`;
          response += `   ⏱️ ${r.prepTime} | 🔥 ${r.calories}\n\n`;
        });
      } else {
        response = `😔 No snack recipes available. But check out our main dishes!`;
      }
    }
    
    // ========== VEGETARIAN/VEGAN QUERIES ==========
    else if (msg.includes('vegetarian') || msg.includes('vegan')) {
      const dietary = msg.includes('vegan') ? 'Vegan' : 'Vegetarian';
      const recipes = await Recipe.find({
        dietaryRestrictions: { $regex: dietary, $options: 'i' }
      }).limit(5);
      
      if (recipes.length > 0) {
        response = `🥗 **${dietary} Recipes** (${recipes.length} found)\n\n`;
        recipes.forEach((r, i) => {
          response += `**${i + 1}. ${r.recipeName}**\n`;
          response += `   🌊 ${r.seaweedType} | ${r.category}\n`;
          response += `   ⏱️ ${r.prepTime} | 🔥 ${r.calories}\n`;
          response += `   ✅ ${r.dietaryRestrictions}\n\n`;
        });
        response += `💡 *Use Smart Recommendations and select ${dietary} to get personalized suggestions!*`;
      } else {
        response = `😔 No ${dietary.toLowerCase()} recipes found at the moment.`;
      }
    }
    
    // ========== QUICK/FAST/EASY QUERIES ==========
    else if (msg.includes('quick') || msg.includes('fast') || msg.includes('easy')) {
      const allRecipes = await Recipe.find().limit(30);
      const quickRecipes = allRecipes.filter(r => {
        const time = parseInt(r.prepTime.replace(/[^\d]/g, ''));
        return time <= 30;
      }).slice(0, 5);
      
      if (quickRecipes.length > 0) {
        response = `⚡ **Quick & Easy Recipes** (${quickRecipes.length} found)\n\n`;
        quickRecipes.forEach((r, i) => {
          response += `**${i + 1}. ${r.recipeName}**\n`;
          response += `   ⏱️ Ready in ${r.prepTime}!\n`;
          response += `   🌊 ${r.seaweedType} | ${r.category}\n`;
          response += `   🔥 ${r.calories}\n\n`;
        });
        response += `💡 *All recipes take 30 minutes or less!*`;
      } else {
        response = `All our recipes are worth the time, but they're delicious! 😊`;
      }
    }
    
    // ========== HIGH PROTEIN QUERIES ==========
    else if (msg.includes('protein') || msg.includes('muscle') || msg.includes('workout')) {
      const allRecipes = await Recipe.find().limit(30);
      const highProteinRecipes = allRecipes.filter(r => {
        const protein = parseInt(r.protein.replace(/[^\d]/g, ''));
        return protein > 10;
      }).slice(0, 5);
      
      if (highProteinRecipes.length > 0) {
        response = `💪 **High Protein Recipes** (${highProteinRecipes.length} found)\n\n`;
        highProteinRecipes.forEach((r, i) => {
          response += `**${i + 1}. ${r.recipeName}**\n`;
          response += `   💪 Protein: ${r.protein}\n`;
          response += `   🌊 ${r.seaweedType} | ${r.category}\n`;
          response += `   ⏱️ ${r.prepTime} | 🔥 ${r.calories}\n\n`;
        });
        response += `💡 *Perfect for muscle building and post-workout meals!*`;
      } else {
        response = `All seaweed is naturally high in protein and nutrients! 🌊`;
      }
    }
    
    // ========== LOW CALORIE / WEIGHT LOSS QUERIES ==========
    else if (msg.includes('low calorie') || msg.includes('weight loss') || msg.includes('diet') || msg.includes('lose weight')) {
      const allRecipes = await Recipe.find().limit(30);
      const lowCalRecipes = allRecipes.filter(r => {
        const calories = parseInt(r.calories.replace(/[^\d]/g, ''));
        return calories < 200;
      }).slice(0, 5);
      
      if (lowCalRecipes.length > 0) {
        response = `🥗 **Low Calorie Recipes** (${lowCalRecipes.length} found)\n\n`;
        lowCalRecipes.forEach((r, i) => {
          response += `**${i + 1}. ${r.recipeName}**\n`;
          response += `   🔥 Only ${r.calories}!\n`;
          response += `   🌊 ${r.seaweedType} | ${r.category}\n`;
          response += `   ⏱️ ${r.prepTime}\n\n`;
        });
        response += `💡 *All recipes under 200 calories - perfect for weight management!*`;
      } else {
        response = `All seaweed recipes are naturally healthy and low in calories! 🌿`;
      }
    }
    
    // ========== SEAWEED TYPE QUERIES ==========
    else if (msg.includes('kappaphycus') || msg.includes('alvarezii')) {
      const recipes = await Recipe.find({ seaweedType: 'Kappaphycus Alvarezii' }).limit(5);
      
      if (recipes.length > 0) {
        response = `🌊 **Kappaphycus Alvarezii Recipes** (${recipes.length} found)\n\n`;
        recipes.forEach((r, i) => {
          response += `**${i + 1}. ${r.recipeName}**\n`;
          response += `   ${r.category} | ⏱️ ${r.prepTime}\n`;
          response += `   🔥 ${r.calories} | ${r.dietaryRestrictions}\n\n`;
        });
        response += `💡 *Kappaphycus Alvarezii is rich in carrageenan and minerals!*`;
      } else {
        response = `Try searching in the recipe dashboard for more Kappaphycus Alvarezii recipes!`;
      }
    }
    
    else if (msg.includes('gracilaria') || msg.includes('edulis')) {
      const recipes = await Recipe.find({ seaweedType: 'Gracilaria Edulis' }).limit(5);
      
      if (recipes.length > 0) {
        response = `🌊 **Gracilaria Edulis Recipes** (${recipes.length} found)\n\n`;
        recipes.forEach((r, i) => {
          response += `**${i + 1}. ${r.recipeName}**\n`;
          response += `   ${r.category} | ⏱️ ${r.prepTime}\n`;
          response += `   🔥 ${r.calories} | ${r.dietaryRestrictions}\n\n`;
        });
        response += `💡 *Gracilaria Edulis is known for its agar content and health benefits!*`;
      } else {
        response = `Check the recipe dashboard for Gracilaria Edulis options!`;
      }
    }
    
    // ========== INGREDIENTS QUERIES ==========
    else if (msg.includes('ingredient') || msg.includes('what can i cook')) {
      response = `🥘 **Looking for recipes by ingredients?**\n\n`;
      response += `Use the **"What Can I Cook?"** tab to:\n`;
      response += `• Enter your available ingredients\n`;
      response += `• See which recipes you can make\n`;
      response += `• Find out what's missing\n`;
      response += `• Get match percentages\n\n`;
      response += `It's super easy - just list what you have!`;
    }
    
    // ========== NUTRITION QUERIES ==========
    else if (msg.includes('nutrition') || msg.includes('healthy') || msg.includes('benefits')) {
      response = `🌿 **Seaweed Nutrition Benefits:**\n\n`;
      response += `Seaweed is incredibly nutritious:\n\n`;
      response += `💪 **High in:**\n`;
      response += `• Protein and amino acids\n`;
      response += `• Vitamins (A, C, E, K, B12)\n`;
      response += `• Minerals (Iodine, Calcium, Iron)\n`;
      response += `• Fiber and Omega-3s\n\n`;
      response += `❤️ **Health Benefits:**\n`;
      response += `• Supports thyroid function\n`;
      response += `• Boosts immune system\n`;
      response += `• Aids digestion\n`;
      response += `• Heart health\n\n`;
      response += `💡 *Try our Smart Recommendations and select "Heart Health" or "Muscle Gain" for specific benefits!*`;
    }
    
    // ========== HELP QUERIES ==========
    else if (msg.includes('help') || msg.includes('what can you do') || msg.includes('commands')) {
      response = `🤖 **I'm Your Seaweed Recipe Assistant!**\n\n`;
      response += `**🍽️ Meal Types:**\n`;
      response += `Ask about: breakfast, lunch, dinner, snacks\n\n`;
      response += `**🥗 Dietary Preferences:**\n`;
      response += `Ask about: vegetarian, vegan recipes\n\n`;
      response += `**⚡ Special Needs:**\n`;
      response += `• Quick & easy recipes\n`;
      response += `• High protein meals\n`;
      response += `• Low calorie options\n\n`;
      response += `**🌊 Seaweed Types:**\n`;
      response += `• Kappaphycus Alvarezii\n`;
      response += `• Gracilaria Edulis\n\n`;
      response += `**💡 Pro Tips:**\n`;
      response += `• Use "Smart Recommendations" for personalized suggestions\n`;
      response += `• Try "What Can I Cook?" to find recipes with your ingredients\n\n`;
      response += `Just ask me anything! 😊`;
    }
    
    // ========== THANK YOU ==========
    else if (msg.includes('thank') || msg.includes('thanks')) {
      response = `You're welcome! 😊\n\n`;
      response += `Happy cooking with seaweed! 🌊\n\n`;
      response += `Feel free to ask me anything else about recipes!`;
    }
    
    // ========== DEFAULT RESPONSE ==========
    else {
      response = `Hi! I'm your seaweed recipe assistant! 🌊\n\n`;
      response += `I can help you find:\n\n`;
      response += `🍳 **Meal Ideas:**\n`;
      response += `• Breakfast, lunch, dinner, snacks\n\n`;
      response += `🥗 **Dietary Options:**\n`;
      response += `• Vegetarian, vegan recipes\n\n`;
      response += `⚡ **Special Requests:**\n`;
      response += `• Quick & easy recipes\n`;
      response += `• High protein meals\n`;
      response += `• Low calorie options\n\n`;
      response += `🌊 **Seaweed Types:**\n`;
      response += `• Kappaphycus Alvarezii\n`;
      response += `• Gracilaria Edulis\n\n`;
      response += `**Try asking:**\n`;
      response += `• "Show me breakfast recipes"\n`;
      response += `• "I want quick recipes"\n`;
      response += `• "High protein meals"\n`;
      response += `• "Vegetarian options"\n\n`;
      response += `What would you like to cook today? 🍽️`;
    }
    
    console.log('✅ Chat response generated');
    
    res.status(200).json({
      success: true,
      response: response,
      message: 'Chat response generated'
    });
    
  } catch (error) {
    console.error('❌ Error in chat:', error);
    res.status(500).json({
      success: false,
      response: 'Sorry, I encountered an error. Please try again! 🙏',
      message: error.message || 'Failed to chat'
    });
  }
};