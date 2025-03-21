from http.server import BaseHTTPRequestHandler
import json
import os
from ski_resort_finder.ski_resort import SkiResortFinder

# Initialize the ski resort finder with the API key
ski_finder = SkiResortFinder(os.environ.get('GOOGLE_MAPS_API_KEY'))

def handle_search(event, context):
    try:
        body = json.loads(event['body'])
        query = body.get('query')
        
        if not query:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No query provided'})
            }
            
        results = ski_finder.find_best_ski_resorts(query)
        
        if not results:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No ski resorts found'})
            }
            
        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handle_test(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({'status': 'ok', 'message': 'Backend is running'})
    }

def handler(event, context):
    if event['path'] == '/api/test':
        return handle_test(event, context)
    elif event['path'] == '/api/search':
        return handle_search(event, context)
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'})
        } 