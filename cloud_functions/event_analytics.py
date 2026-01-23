import functions_framework
from datetime import datetime
import json

@functions_framework.http
def event_analytics(request):
    """
    Cloud Function: Calculate event analytics and popularity metrics
    
    This function analyzes event performance and returns metrics.
    Can be called periodically or on-demand to generate reports.
    
    Expected query parameters:
    - event_id (optional): Specific event ID to analyze
    - days (optional): Number of days to analyze (default: 30)
    """
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    if request.method == 'OPTIONS':
        return ('', 204, headers)

    try:
        # Get parameters
        args = request.args
        event_id = args.get('event_id', None)
        days = int(args.get('days', 30))
        
        # Simulate analytics calculation
        # In production, this would query actual database
        analytics_data = {
            'success': True,
            'period_days': days,
            'metrics': {
                'total_bookings': 45,
                'total_revenue': 3375.00,
                'average_booking_value': 75.00,
                'popular_categories': [
                    {'category': 'Conference', 'bookings': 20},
                    {'category': 'Concert', 'bookings': 15},
                    {'category': 'Workshop', 'bookings': 10}
                ],
                'peak_booking_hours': [
                    {'hour': 14, 'bookings': 12},
                    {'hour': 10, 'bookings': 10},
                    {'hour': 16, 'bookings': 8}
                ],
                'conversion_rate': 0.65,
                'average_tickets_per_booking': 2.3
            },
            'generated_at': datetime.now().isoformat()
        }
        
        if event_id:
            analytics_data['event_id'] = event_id
            analytics_data['event_specific'] = {
                'views': 234,
                'bookings': 45,
                'conversion_rate': 0.19,
                'revenue': 3375.00,
                'avg_rating': 4.5
            }
        
        print(f"Analytics generated for period: {days} days")
        
        return (json.dumps(analytics_data), 200, headers)
    
    except Exception as e:
        return (json.dumps({
            'success': False,
            'error': str(e)
        }), 500, headers)