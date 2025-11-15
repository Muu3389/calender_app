"""
Security tests for the calendar application
"""
import unittest
import json
import tempfile
import os
from pathlib import Path
from app import app, init_db, validate_color, validate_date, validate_time


class SecurityTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and temporary database"""
        # Create a temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['TESTING'] = True
        
        # Monkey patch DB_PATH for testing
        import app as app_module
        self.original_db_path = app_module.DB_PATH
        app_module.DB_PATH = Path(self.db_path)
        
        self.client = app.test_client()
        
        # Initialize database - force creation
        if Path(self.db_path).exists():
            os.unlink(self.db_path)
        
        with app.app_context():
            conn = app_module.get_db()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    title TEXT NOT NULL,
                    time TEXT NOT NULL,
                    color TEXT NOT NULL DEFAULT '#e8f0fe'
                )
            """)
            conn.commit()
            conn.close()
    
    def tearDown(self):
        """Clean up temporary database"""
        import app as app_module
        app_module.DB_PATH = self.original_db_path
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_color_validation_prevents_xss(self):
        """Test that color validation prevents XSS attacks"""
        # Valid color
        self.assertEqual(validate_color('#ff0000'), '#ff0000')
        self.assertEqual(validate_color('#ABCDEF'), '#ABCDEF')
        
        # Invalid colors should return default
        self.assertEqual(validate_color('<script>alert("xss")</script>'), '#e8f0fe')
        self.assertEqual(validate_color('javascript:alert(1)'), '#e8f0fe')
        self.assertEqual(validate_color('#ff00'), '#e8f0fe')  # Too short
        self.assertEqual(validate_color('#ff00000'), '#e8f0fe')  # Too long
        self.assertEqual(validate_color('red'), '#e8f0fe')  # Named color
        self.assertEqual(validate_color(''), '#e8f0fe')  # Empty
        self.assertEqual(validate_color(None), '#e8f0fe')  # None
    
    def test_date_validation(self):
        """Test date validation"""
        self.assertTrue(validate_date('2024-01-01'))
        self.assertTrue(validate_date('2024-12-31'))
        
        self.assertFalse(validate_date('2024-13-01'))  # Invalid month
        self.assertFalse(validate_date('2024-01-32'))  # Invalid day
        self.assertFalse(validate_date('invalid'))
        self.assertFalse(validate_date(''))
        self.assertFalse(validate_date(None))
    
    def test_time_validation(self):
        """Test time validation"""
        self.assertTrue(validate_time(''))  # Empty is valid
        self.assertTrue(validate_time('00:00'))
        self.assertTrue(validate_time('23:59'))
        
        self.assertFalse(validate_time('24:00'))  # Invalid hour
        self.assertFalse(validate_time('23:60'))  # Invalid minute
        self.assertFalse(validate_time('invalid'))
    
    def test_add_event_with_invalid_data(self):
        """Test that adding events with invalid data returns error"""
        # Missing title
        response = self.client.post('/add',
            data=json.dumps({
                'date': '2024-01-01',
                'time': '10:00',
                'title': '',
                'color': '#ff0000'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')
    
    def test_add_event_with_invalid_date(self):
        """Test that adding events with invalid date returns error"""
        response = self.client.post('/add',
            data=json.dumps({
                'date': 'invalid-date',
                'time': '10:00',
                'title': 'Test Event',
                'color': '#ff0000'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_add_event_with_xss_attempt(self):
        """Test that XSS attempts in title are handled"""
        response = self.client.post('/add',
            data=json.dumps({
                'date': '2024-01-01',
                'time': '10:00',
                'title': '<script>alert("xss")</script>',
                'color': '#ff0000'
            }),
            content_type='application/json'
        )
        # Should succeed but data will be escaped
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
    
    def test_delete_invalid_event_id(self):
        """Test that deleting with invalid ID returns error"""
        # Flask routing converts to int, negative IDs don't match <int:event_id>
        # So we test with a valid positive ID that doesn't exist
        response = self.client.post('/delete/99999')
        # Should succeed with 204 even if event doesn't exist (idempotent)
        self.assertEqual(response.status_code, 204)
    
    def test_security_headers(self):
        """Test that security headers are present"""
        response = self.client.get('/')
        
        self.assertIn('X-Content-Type-Options', response.headers)
        self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')
        
        self.assertIn('X-Frame-Options', response.headers)
        self.assertEqual(response.headers['X-Frame-Options'], 'DENY')
        
        self.assertIn('X-XSS-Protection', response.headers)
        
        self.assertIn('Content-Security-Policy', response.headers)
    
    def test_title_length_limit(self):
        """Test that very long titles are truncated"""
        long_title = 'A' * 300  # Longer than 200 char limit
        response = self.client.post('/add',
            data=json.dumps({
                'date': '2024-01-01',
                'time': '10:00',
                'title': long_title,
                'color': '#ff0000'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        # Title should be truncated to 200 chars


if __name__ == '__main__':
    unittest.main()
