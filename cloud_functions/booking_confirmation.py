import functions_framework
from datetime import datetime
import json

@functions_framework.http
def booking_confirmation(request):
    """
    Cloud Function: Process booking confirmation and send email notification
    
    Triggered when a new booking is made.
    In production, this would integrate with SendGrid/Mailgun to send emails.
    
    Expected request body:
    {
        "booking_id": "123",
        "user_email": "user@example.com",
        "event_name": "Tech Summit 2025",
        "tickets": 2,
        "total_price": 150.00
    }
    """
    
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    try:
        request_json = request.get_json(silent=True)
        
        if not request_json:
            return (json.dumps({
                'success': False,
                'error': 'No data provided'
            }), 400, headers)
        
        # Extract booking details
        booking_id = request_json.get('booking_id')
        user_email = request_json.get('user_email')
        event_name = request_json.get('event_name')
        tickets = request_json.get('tickets')
        total_price = request_json.get('total_price')
        
        # Validate required fields
        if not all([booking_id, user_email, event_name, tickets, total_price]):
            return (json.dumps({
                'success': False,
                'error': 'Missing required fields'
            }), 400, headers)
        
        # Simulate email sending (in production, integrate with SendGrid/Mailgun)
        email_content = f"""
        Booking Confirmation - BookIt
        
        Dear Customer,
        
        Your booking has been confirmed!
        
        Booking Details:
        - Booking ID: {booking_id}
        - Event: {event_name}
        - Number of Tickets: {tickets}
        - Total Amount: ${total_price}
        - Confirmation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Your e-tickets have been generated and are available in your account.
        
        Thank you for using BookIt!
        
        Best regards,
        BookIt Team
        """
        
        # Log the email (in production, this would send actual email)
        print(f"Email sent to {user_email}")
        print(email_content)
        
        # Return success response
        response_data = {
            'success': True,
            'message': 'Booking confirmation processed successfully',
            'booking_id': booking_id,
            'email_sent_to': user_email,
            'timestamp': datetime.now().isoformat()
        }
        
        return (json.dumps(response_data), 200, headers)
    
    except Exception as e:
        return (json.dumps({
            'success': False,
            'error': str(e)
        }), 500, headers)