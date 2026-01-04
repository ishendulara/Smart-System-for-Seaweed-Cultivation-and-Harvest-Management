#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get AI Recommendations Script - Fixed Encoding
"""

import sys
import json
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.aiService import ai_service
except ImportError as e:
    print(json.dumps({
        'success': False,
        'error': f'Failed to import AI service: {str(e)}',
        'recommendations': []
    }))
    sys.exit(1)

def get_recommendations(preferences):
    """
    Get AI-powered recipe recommendations
    """
    try:
        recommendations = ai_service.get_recommendations(preferences)
        
        # Format response
        formatted_recommendations = []
        for rec in recommendations:
            formatted_recommendations.append({
                'recipeId': rec['recipe_id'],
                'recipeName': rec['recipe_name'],
                'seaweedType': rec['seaweed_type'],
                'category': rec['category'],
                'prepTime': rec['prep_time'],
                'servings': rec['servings'],
                'dietaryRestrictions': rec['dietary_restrictions'],
                'ingredients': rec['ingredients'],
                'howToMake': rec['how_to_make'],
                'calories': rec['calories'],
                'protein': rec['protein'],
                'carbohydrates': rec['carbohydrates'],
                'fiber': rec['fiber'],
                'fat': rec['fat'],
                'minerals': rec['minerals'],
                'score': round(rec['final_score'], 2),
                'reason': rec['reason'],
                'healthBenefits': rec['health_benefits'],
                'matchingPreferences': rec['matching_preferences']
            })
        
        return {
            'success': True,
            'recommendations': formatted_recommendations,
            'count': len(formatted_recommendations)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'recommendations': []
        }

if __name__ == '__main__':
    try:
        # Get preferences from command line argument
        if len(sys.argv) < 2:
            print(json.dumps({
                'success': False,
                'error': 'No preferences provided',
                'recommendations': []
            }))
            sys.exit(1)
        
        preferences_json = sys.argv[1]
        preferences = json.loads(preferences_json)
        
        # Get recommendations
        result = get_recommendations(preferences)
        
        # Output as JSON with UTF-8 encoding
        print(json.dumps(result, ensure_ascii=False))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            'success': False,
            'error': f'Invalid JSON: {str(e)}',
            'recommendations': []
        }))
        sys.exit(1)
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e),
            'recommendations': []
        }))
        sys.exit(1)