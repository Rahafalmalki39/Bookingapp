import unittest
from main import app
import json

class BookItTestCase(unittest.TestCase):
    """Unit tests for BookIt application"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_homepage_loads(self):
        """Test that homepage loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BookIt', response.data)
    
    def test_events_page_loads(self):
        """Test that events page loads successfully"""
        response = self.client.get('/events')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Events', response.data)
    
    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_register_page_loads(self):
        """Test that register page loads successfully"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)
    
    def test_chat_page_loads(self):
        """Test that chat page loads successfully"""
        response = self.client.get('/chat')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Assistant', response.data)
    
    def test_api_events_endpoint(self):
        """Test REST API events endpoint returns JSON"""
        response = self.client.get('/api/events')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('events', data)
    
    def test_api_stats_endpoint(self):
        """Test REST API stats endpoint returns JSON"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('statistics', data)
    
    def test_api_chat_endpoint(self):
        """Test chatbot API endpoint"""
        response = self.client.post('/api/chat',
                                   data=json.dumps({'message': 'hello'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('message', data)
    
    def test_api_chat_empty_message(self):
        """Test chatbot API with empty message returns error"""
        response = self.client.post('/api/chat',
                                   data=json.dumps({'message': ''}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_event_not_found(self):
        """Test accessing non-existent event returns 404"""
        response = self.client.get('/event/nonexistent123')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()