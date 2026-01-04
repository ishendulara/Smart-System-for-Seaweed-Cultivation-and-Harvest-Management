# backend/services/aiService.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced AI Recipe Service - Fixed Encoding
"""

import pickle
import json
import numpy as np
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError as e:
    print(json.dumps({
        'success': False,
        'error': f'Missing required package: {str(e)}. Please run: pip install sentence-transformers scikit-learn',
        'recommendations': []
    }))
    sys.exit(1)

class EnhancedAIRecipeService:
    def __init__(self):
        """
        Initialize the enhanced AI service with new format
        """
        # Paths
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(self.base_path, '..', 'models')
        
        # Models
        self.model = None
        self.embeddings = None
        self.recipes_data = None
        
        # Load everything
        self.load_model()
    
    def load_model(self):
        """
        Load pre-trained model and NEW format data
        """
        try:
            print(json.dumps({'status': 'loading', 'message': 'Loading AI models...'}), file=sys.stderr)
            
            # 1. Load SentenceTransformer model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print(json.dumps({'status': 'success', 'message': 'Sentence Transformer loaded'}), file=sys.stderr)
            
            # 2. Load embeddings
            embeddings_path = os.path.join(self.model_path, 'recipe_embeddings.pkl')
            
            if not os.path.exists(embeddings_path):
                raise FileNotFoundError(f'Embeddings file not found: {embeddings_path}')
            
            with open(embeddings_path, 'rb') as f:
                self.embeddings = pickle.load(f)
            print(json.dumps({'status': 'success', 'message': f'Embeddings loaded: {self.embeddings.shape}'}), file=sys.stderr)
            
            # 3. Load NEW format recipe data with proper encoding
            recipes_path = os.path.join(self.model_path, 'recipes_data.json')
            
            if not os.path.exists(recipes_path):
                raise FileNotFoundError(f'Recipes file not found: {recipes_path}')
            
            with open(recipes_path, 'r', encoding='utf-8') as f:
                self.recipes_data = json.load(f)
            print(json.dumps({'status': 'success', 'message': f'Recipes loaded: {len(self.recipes_data)}'}), file=sys.stderr)
            
        except FileNotFoundError as e:
            error_msg = {
                'success': False,
                'error': f'Required files not found: {str(e)}',
                'recommendations': []
            }
            print(json.dumps(error_msg))
            sys.exit(1)
            
        except Exception as e:
            error_msg = {
                'success': False,
                'error': f'Error loading model: {str(e)}',
                'recommendations': []
            }
            print(json.dumps(error_msg))
            sys.exit(1)
    
    def get_recommendations(self, preferences):
        """
        Get AI-powered recommendations with NEW filtering options
        """
        try:
            # Build search query
            query_parts = []
            
            if preferences.get('seaweedType'):
                query_parts.append(preferences['seaweedType'])
            
            if preferences.get('dietaryRestrictions'):
                query_parts.extend(preferences['dietaryRestrictions'])
            
            if preferences.get('healthGoals'):
                query_parts.extend(preferences['healthGoals'])
            
            if preferences.get('preferredMealType') and preferences['preferredMealType'] != 'any':
                query_parts.append(preferences['preferredMealType'])
            
            # Create query text
            query = ' '.join(query_parts).lower()
            
            # Get similar recipes using AI
            similar_recipes = self._find_similar_recipes(query, top_k=30)
            
            # Filter by seaweed type
            if preferences.get('seaweedType'):
                similar_recipes = [
                    r for r in similar_recipes 
                    if r['seaweed_type'] == preferences['seaweedType']
                ]
            
            # Filter by category
            if preferences.get('preferredMealType') and preferences['preferredMealType'] != 'any':
                similar_recipes = [
                    r for r in similar_recipes 
                    if r.get('category', '').lower() == preferences['preferredMealType'].lower()
                ]
            
            # Filter by dietary restrictions
            if preferences.get('dietaryRestrictions'):
                filtered = []
                for recipe in similar_recipes:
                    dietary = recipe.get('dietary_restrictions', '').lower()
                    if any(d.lower() in dietary for d in preferences['dietaryRestrictions']):
                        filtered.append(recipe)
                if filtered:
                    similar_recipes = filtered
            
            # Score and rank
            scored_recipes = self._score_recommendations(similar_recipes, preferences)
            
            # Return top 5
            return scored_recipes
            
        except Exception as e:
            print(json.dumps({'error': f'Recommendation error: {str(e)}'}), file=sys.stderr)
            return []
    
    def _find_similar_recipes(self, query, top_k=10):
        """
        Find similar recipes using semantic search
        """
        # Encode the query
        query_embedding = self.model.encode([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top k indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # Build results
        results = []
        for idx in top_indices:
            recipe = self.recipes_data[idx]
            results.append({
                'recipe_id': int(idx),
                'recipe_name': recipe.get('Recipe Name', ''),
                'seaweed_type': recipe.get('Seaweed Type', ''),
                'category': recipe.get('Category', ''),
                'prep_time': recipe.get('Prep Time', ''),
                'servings': recipe.get('Servings', ''),
                'dietary_restrictions': recipe.get('Dietary Restrictions', ''),
                'ingredients': recipe.get('Ingredients', ''),
                'how_to_make': recipe.get('How to Make', ''),
                'calories': recipe.get('Calories', ''),
                'protein': recipe.get('Protein', ''),
                'carbohydrates': recipe.get('Carbohydrates', ''),
                'fiber': recipe.get('Fiber', ''),
                'fat': recipe.get('Fat', ''),
                'minerals': recipe.get('Minerals', ''),
                'similarity_score': float(similarities[idx])
            })
        
        return results
    
    def _score_recommendations(self, recommendations, preferences):
        """
        Score and rank recommendations
        """
        for rec in recommendations:
            # Start with similarity score (0-100)
            score = rec['similarity_score'] * 100
            
            ingredients_lower = rec['ingredients'].lower()
            dietary = rec.get('dietary_restrictions', '').lower()
            
            # Bonus for dietary restrictions match
            restrictions = preferences.get('dietaryRestrictions', [])
            for restriction in restrictions:
                if restriction.lower() in dietary:
                    score += 15
            
            # Bonus for health goals
            goals = preferences.get('healthGoals', [])
            
            if 'Weight Loss' in goals:
                try:
                    calories = int(''.join(filter(str.isdigit, rec.get('calories', '0'))))
                    if calories < 200:
                        score += 15
                except:
                    pass
            
            if 'Muscle Gain' in goals:
                try:
                    protein_str = rec.get('protein', '0').split('g')[0]
                    protein = int(''.join(filter(str.isdigit, protein_str)))
                    if protein > 10:
                        score += 15
                except:
                    pass
            
            # Cap at 100
            rec['final_score'] = min(score, 100)
            rec['reason'] = self._generate_reason(rec, preferences)
            rec['health_benefits'] = self._extract_health_benefits(rec)
            rec['matching_preferences'] = self._get_matching_preferences(rec, preferences)
        
        # Sort by final score
        recommendations.sort(key=lambda x: x['final_score'], reverse=True)
        
        return recommendations
    
    def _generate_reason(self, recipe, preferences):
        """
        Generate explanation for recommendation
        """
        reasons = []
        
        if preferences.get('seaweedType') == recipe['seaweed_type']:
            reasons.append(f"Contains your preferred {recipe['seaweed_type']}")
        
        if recipe.get('category'):
            reasons.append(f"Perfect for {recipe['category']}")
        
        if recipe.get('dietary_restrictions'):
            reasons.append(f"{recipe['dietary_restrictions']} friendly")
        
        return ' | '.join(reasons) if reasons else "Popular and nutritious recipe"
    
    def _extract_health_benefits(self, recipe):
        """
        Extract health benefits
        """
        benefits = []
        
        try:
            protein = int(''.join(filter(str.isdigit, recipe.get('protein', '0').split('g')[0])))
            if protein > 5:
                benefits.append('High Protein')
        except:
            pass
        
        try:
            fiber = int(''.join(filter(str.isdigit, recipe.get('fiber', '0').split('g')[0])))
            if fiber > 3:
                benefits.append('Rich in Fiber')
        except:
            pass
        
        minerals = recipe.get('minerals', '').lower()
        if 'vitamin' in minerals:
            benefits.append('Vitamin Rich')
        if 'calcium' in minerals or 'iron' in minerals:
            benefits.append('Mineral Rich')
        
        return benefits[:4]
    
    def _get_matching_preferences(self, recipe, preferences):
        """
        Get matching preferences
        """
        matches = []
        
        if preferences.get('seaweedType') == recipe['seaweed_type']:
            matches.append('Seaweed Type')
        
        if preferences.get('preferredMealType') and preferences['preferredMealType'].lower() in recipe.get('category', '').lower():
            matches.append('Meal Type')
        
        if preferences.get('dietaryRestrictions'):
            matches.append('Dietary Needs')
        
        return matches

# Global instance
try:
    ai_service = EnhancedAIRecipeService()
except Exception as e:
    print(json.dumps({
        'success': False,
        'error': f'Failed to initialize AI service: {str(e)}',
        'recommendations': []
    }))
    sys.exit(1)