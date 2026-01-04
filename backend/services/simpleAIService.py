# backend/services/simpleAIService.py
import json
import os

class SimpleAIRecipeService:
    def __init__(self):
        self.recipes = []
        self.load_recipes()
    
    def load_recipes(self):
        """Load recipes from MongoDB via API"""
        print("✅ Simple AI Service initialized (No ML)")
        
    def get_recommendations(self, preferences):
        """Simple rule-based recommendations"""
        # Return sample data for testing
        return [
            {
                'recipe_name': 'Seaweed Soup',
                'final_score': 95,
                'reason': 'Popular recipe',
                'health_benefits': ['High Protein', 'Vitamins']
            }
        ]
    
    def suggest_by_ingredients(self, ingredients, seaweed_type=None):
        """Simple ingredient matching"""
        return [
            {
                'recipe_name': 'Seaweed Salad',
                'match_percentage': 80,
                'missing_ingredients': ['vinegar'],
                'reason': 'You have most ingredients'
            }
        ]
    
    def chat_response(self, message):
        """Simple chat responses"""
        if 'recipe' in message.lower():
            return "I can help you find seaweed recipes! What type of dish are you looking for?"
        return "I'm here to help with seaweed recipes. What would you like to know?"

# Global instance
ai_service = SimpleAIRecipeService()