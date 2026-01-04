# backend/services/nutritional_analysis.py
#!/usr/bin/env python3
"""
Nutritional Analysis Script
Analyzes recipe nutrition from Enhanced AI Recipe Service
"""

import sys
import json
import os
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.aiService import ai_service

def extract_number(value):
    """Extract numeric value from string like '250 kcal' or '15g'"""
    if not value:
        return 0
    match = re.search(r'(\d+(?:\.\d+)?)', str(value))
    return float(match.group(1)) if match else 0

def analyze_nutrition(recipe_id=None, recipe_data=None):
    """
    Analyze nutritional content of a recipe
    
    Args:
        recipe_id (int): Recipe ID from database
        recipe_data (dict): Or direct recipe data
    
    Returns:
        dict: Nutritional analysis
    """
    try:
        # Get recipe data
        if recipe_data:
            recipe = recipe_data
        elif recipe_id is not None:
            if recipe_id < 0 or recipe_id >= len(ai_service.recipes_data):
                return {
                    'success': False,
                    'error': 'Recipe not found'
                }
            recipe = ai_service.recipes_data[recipe_id]
        else:
            return {
                'success': False,
                'error': 'No recipe specified'
            }
        
        # Extract nutritional values
        calories = extract_number(recipe.get('Calories', '0'))
        protein = extract_number(recipe.get('Protein', '0'))
        carbs = extract_number(recipe.get('Carbohydrates', '0'))
        fiber = extract_number(recipe.get('Fiber', '0'))
        fat = extract_number(recipe.get('Fat', '0'))
        
        # Calculate percentages of daily values (based on 2000 kcal diet)
        daily_values = {
            'calories': round((calories / 2000) * 100, 1),
            'protein': round((protein / 50) * 100, 1),  # 50g daily value
            'carbs': round((carbs / 300) * 100, 1),  # 300g daily value
            'fiber': round((fiber / 25) * 100, 1),  # 25g daily value
            'fat': round((fat / 70) * 100, 1)  # 70g daily value
        }
        
        # Determine nutritional profile
        profile = []
        if protein >= 15:
            profile.append('High Protein')
        if fiber >= 5:
            profile.append('High Fiber')
        if calories < 200:
            profile.append('Low Calorie')
        if fat < 5:
            profile.append('Low Fat')
        
        # Health score (0-100)
        health_score = 0
        health_score += min(protein * 2, 30)  # Protein contributes up to 30 points
        health_score += min(fiber * 4, 25)  # Fiber contributes up to 25 points
        health_score += max(0, 20 - (fat * 2))  # Low fat bonus up to 20 points
        health_score += max(0, 25 - (calories / 10))  # Low calorie bonus up to 25 points
        health_score = min(round(health_score), 100)
        
        # Extract minerals and vitamins
        minerals_raw = recipe.get('Minerals', '')
        minerals_list = [m.strip() for m in minerals_raw.split(',') if m.strip()]
        
        # Categorize minerals
        vitamins = [m for m in minerals_list if 'vitamin' in m.lower()]
        minerals = [m for m in minerals_list if 'vitamin' not in m.lower()]
        
        # Dietary tags
        dietary = recipe.get('Dietary Restrictions', '').split(',')
        dietary_tags = [d.strip() for d in dietary if d.strip() and d.strip().lower() != 'none']
        
        # Build analysis result
        analysis = {
            'success': True,
            'recipeName': recipe.get('Recipe Name', ''),
            'seaweedType': recipe.get('Seaweed Type', ''),
            'category': recipe.get('Category', ''),
            'nutrition': {
                'calories': calories,
                'protein': f"{protein}g",
                'carbohydrates': f"{carbs}g",
                'fiber': f"{fiber}g",
                'fat': f"{fat}g"
            },
            'dailyValues': daily_values,
            'nutritionalProfile': profile if profile else ['Balanced'],
            'healthScore': health_score,
            'vitamins': vitamins,
            'minerals': minerals,
            'dietaryTags': dietary_tags,
            'servings': recipe.get('Servings', ''),
            'prepTime': recipe.get('Prep Time', ''),
            'recommendations': []
        }
        
        # Add recommendations based on nutritional content
        if health_score >= 75:
            analysis['recommendations'].append('Excellent nutritional profile - great for regular consumption')
        if protein >= 15:
            analysis['recommendations'].append('High protein content - ideal for muscle building')
        if fiber >= 5:
            analysis['recommendations'].append('Rich in fiber - supports digestive health')
        if calories < 200:
            analysis['recommendations'].append('Low calorie option - suitable for weight management')
        if minerals:
            analysis['recommendations'].append(f'Rich in essential minerals - supports overall health')
        
        return analysis
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def compare_recipes(recipe_ids):
    """
    Compare nutritional content of multiple recipes
    
    Args:
        recipe_ids (list): List of recipe IDs to compare
    
    Returns:
        dict: Comparison results
    """
    try:
        if not recipe_ids or len(recipe_ids) < 2:
            return {
                'success': False,
                'error': 'At least 2 recipes required for comparison'
            }
        
        analyses = []
        for recipe_id in recipe_ids:
            analysis = analyze_nutrition(recipe_id=recipe_id)
            if analysis['success']:
                analyses.append(analysis)
        
        if len(analyses) < 2:
            return {
                'success': False,
                'error': 'Could not analyze enough recipes'
            }
        
        # Find best in each category
        best = {
            'highestProtein': max(analyses, key=lambda x: extract_number(x['nutrition']['protein']))['recipeName'],
            'highestFiber': max(analyses, key=lambda x: extract_number(x['nutrition']['fiber']))['recipeName'],
            'lowestCalories': min(analyses, key=lambda x: x['nutrition']['calories'])['recipeName'],
            'highestHealthScore': max(analyses, key=lambda x: x['healthScore'])['recipeName']
        }
        
        return {
            'success': True,
            'recipes': analyses,
            'comparison': best,
            'count': len(analyses)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print(json.dumps({
                'success': False,
                'error': 'No data provided'
            }))
            sys.exit(1)
        
        data_json = sys.argv[1]
        data = json.loads(data_json)
        
        # Check if it's a comparison or single analysis
        if 'recipeIds' in data and isinstance(data['recipeIds'], list):
            result = compare_recipes(data['recipeIds'])
        else:
            recipe_id = data.get('recipeId')
            recipe_data = data.get('recipeData')
            result = analyze_nutrition(recipe_id=recipe_id, recipe_data=recipe_data)
        
        print(json.dumps(result))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            'success': False,
            'error': f'Invalid JSON: {str(e)}'
        }))
        sys.exit(1)
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }))
        sys.exit(1)