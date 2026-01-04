# backend/services/suggest_by_ingredients.py
#!/usr/bin/env python3
"""
Suggest Recipes by Available Ingredients Script
Interfaces with Enhanced AI Recipe Service
Usage: python suggest_by_ingredients.py '{"ingredients": ["tomato", "garlic"], "seaweedType": "Nori"}'
"""

import sys
import json
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.aiService import ai_service
except ImportError:
    print(json.dumps({
        'success': False,
        'error': 'Failed to import AI service. Make sure aiService.py exists.'
    }))
    sys.exit(1)

def suggest_by_ingredients(data):
    """
    Suggest recipes based on available ingredients
    
    Args:
        data (dict): {
            'ingredients': list of ingredient names,
            'seaweedType': optional seaweed type filter,
            'category': optional category filter
        }
    
    Returns:
        dict: Suggestion results with matching recipes
    """
    try:
        ingredients = data.get('ingredients', [])
        seaweed_type = data.get('seaweedType')
        category = data.get('category')
        
        # Validate input
        if not ingredients:
            return {
                'success': False,
                'error': 'No ingredients provided',
                'suggestions': []
            }
        
        if not isinstance(ingredients, list):
            return {
                'success': False,
                'error': 'Ingredients must be a list',
                'suggestions': []
            }
        
        # Get suggestions from AI service
        suggestions = ai_service.suggest_by_ingredients(
            ingredients,
            seaweed_type=seaweed_type,
            category=category
        )
        
        # Format response for frontend
        formatted_suggestions = []
        for sug in suggestions:
            formatted_suggestions.append({
                'recipeId': sug['recipe_id'],
                'recipeName': sug['recipe_name'],
                'seaweedType': sug['seaweed_type'],
                'category': sug['category'],
                'prepTime': sug['prep_time'],
                'calories': sug['calories'],
                'dietaryRestrictions': sug['dietary_restrictions'],
                'matchCount': sug['match_count'],
                'matchPercentage': round(sug['match_percentage'], 1),
                'missingIngredients': sug['missing_ingredients'],
                'reason': sug['reason'],
                'recipe': {
                    'ingredients': sug['recipe'].get('Ingredients', ''),
                    'howToMake': sug['recipe'].get('How to Make', ''),
                    'protein': sug['recipe'].get('Protein', ''),
                    'fiber': sug['recipe'].get('Fiber', ''),
                    'minerals': sug['recipe'].get('Minerals', ''),
                    'servings': sug['recipe'].get('Servings', ''),
                    'carbohydrates': sug['recipe'].get('Carbohydrates', ''),
                    'fat': sug['recipe'].get('Fat', '')
                }
            })
        
        return {
            'success': True,
            'suggestions': formatted_suggestions,
            'count': len(formatted_suggestions),
            'searchedIngredients': ingredients,
            'filters': {
                'seaweedType': seaweed_type,
                'category': category
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error processing ingredients: {str(e)}',
            'suggestions': []
        }

if __name__ == '__main__':
    try:
        # Get data from command line argument
        if len(sys.argv) < 2:
            print(json.dumps({
                'success': False,
                'error': 'No data provided. Usage: python suggest_by_ingredients.py \'{"ingredients": ["tomato"]}\''
            }))
            sys.exit(1)
        
        data_json = sys.argv[1]
        data = json.loads(data_json)
        
        # Get suggestions
        result = suggest_by_ingredients(data)
        
        # Output as JSON
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            'success': False,
            'error': f'Invalid JSON format: {str(e)}'
        }))
        sys.exit(1)
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }))
        sys.exit(1)