# backend/services/chat.py
#!/usr/bin/env python3
"""
AI Chat Response Script
Interfaces with Enhanced AI Recipe Service
Usage: python chat.py '{"message": "What are some breakfast recipes?"}'
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
except ImportError:
    print(json.dumps({
        'success': False,
        'error': 'Failed to import AI service. Make sure aiService.py exists.',
        'response': 'AI service is not available.'
    }))
    sys.exit(1)

def chat_with_ai(message):
    """
    Generate AI chat response for recipe queries
    
    Args:
        message (str): User's chat message/question
    
    Returns:
        dict: Chat response with recipe suggestions or information
    """
    try:
        # Validate message
        if not message or not message.strip():
            return {
                'success': False,
                'error': 'Empty message',
                'response': 'Please ask me something about seaweed recipes! 🌊\n\nYou can ask about:\n• Breakfast, lunch, or dinner ideas\n• Vegetarian or vegan recipes\n• Quick and easy recipes\n• High protein meals\n• Specific ingredients'
            }
        
        message = message.strip()
        
        # Get response from AI service
        response = ai_service.chat_response(message)
        
        return {
            'success': True,
            'response': response,
            'message': message,
            'timestamp': None  # Can add timestamp if needed
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'response': 'Sorry, I encountered an error while processing your request. Please try again! 🙏'
        }

def get_quick_suggestions(query_type):
    """
    Get quick recipe suggestions for common queries
    
    Args:
        query_type (str): Type of suggestion (breakfast, lunch, dinner, etc.)
    
    Returns:
        list: Quick recipe suggestions
    """
    try:
        query_type = query_type.lower()
        recipes = []
        
        if query_type in ['breakfast', 'lunch', 'dinner', 'snack', 'dessert']:
            recipes = [
                r for r in ai_service.recipes_data 
                if r.get('Category', '').lower() == query_type
            ][:5]
        
        return [
            {
                'name': r.get('Recipe Name'),
                'seaweed': r.get('Seaweed Type'),
                'time': r.get('Prep Time'),
                'calories': r.get('Calories')
            }
            for r in recipes
        ]
        
    except Exception as e:
        return []

if __name__ == '__main__':
    try:
        # Get message from command line argument
        if len(sys.argv) < 2:
            print(json.dumps({
                'success': False,
                'error': 'No message provided. Usage: python chat.py \'{"message": "your question"}\'',
                'response': 'Please provide a message to chat with the AI.'
            }))
            sys.exit(1)
        
        # Parse input JSON
        data_json = sys.argv[1]
        data = json.loads(data_json)
        
        # Extract message
        message = data.get('message', '')
        
        # Get chat response
        result = chat_with_ai(message)
        
        # Output as JSON with proper formatting
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            'success': False,
            'error': f'Invalid JSON format: {str(e)}',
            'response': 'Failed to parse your message. Please send valid JSON.'
        }))
        sys.exit(1)
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'response': 'An unexpected error occurred. Please try again.'
        }))
        sys.exit(1)