import unittest
import json
from app import app
from database.db import query_db, execute_db, init_db

class RecipeAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with app.app_context():
            init_db()

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_01_home_page(self):
        """Test home page loads with status 200 and displays project branding."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI-Crafted Culinary Magic', response.data)
        self.assertIn(b'Royal Hyderabadi Chicken Biryani', response.data)

    def test_02_login_and_auth(self):
        """Test user login with pre-seeded demo user."""
        response = self.client.post('/login', data={
            'email': 'demo@recipeai.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back', response.data)

    def test_03_registration(self):
        """Test registration of a new user."""
        test_email = 'student2026@recipeai.com'
        # Clean up if existed
        execute_db("DELETE FROM users WHERE email = %s", (test_email,))
        
        response = self.client.post('/register', data={
            'name': 'BCA Project Evaluator',
            'email': test_email,
            'password': 'evaluatorpass',
            'confirm_password': 'evaluatorpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)
        
        # Verify user exists in database
        user = query_db("SELECT * FROM users WHERE email = %s", (test_email,), one=True)
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], 'BCA Project Evaluator')

    def test_04_favourites_lifecycle(self):
        """Test adding and removing a recipe from favourites."""
        # Use client session context
        with self.client:
            login_res = self.client.post('/login', data={
                'email': 'demo@recipeai.com',
                'password': 'password123'
            }, follow_redirects=True)
            self.assertEqual(login_res.status_code, 200)

            # Add recipe 1 to favourites via AJAX
            fav_toggle_res = self.client.post('/favourite/toggle/1', headers={'X-Requested-With': 'XMLHttpRequest'})
            self.assertEqual(fav_toggle_res.status_code, 200)
            data = json.loads(fav_toggle_res.data)
            self.assertTrue(data['success'])

            # Check favourites page
            fav_page = self.client.get('/favourites')
            self.assertEqual(fav_page.status_code, 200)
            self.assertIn(b'Royal Hyderabadi Chicken Biryani', fav_page.data)

            # Toggle again to remove
            fav_toggle_res2 = self.client.post('/favourite/toggle/1', headers={'X-Requested-With': 'XMLHttpRequest'})
            self.assertEqual(fav_toggle_res2.status_code, 200)
            data2 = json.loads(fav_toggle_res2.data)
            self.assertTrue(data2['success'])
            self.assertFalse(data2['is_favourite'])

    def test_05_search_and_history(self):
        """Test recipe search and search history recording."""
        with self.client:
            self.client.post('/login', data={
                'email': 'demo@recipeai.com',
                'password': 'password123'
            })

            # Perform search
            search_res = self.client.post('/search', data={
                'query': 'Vegetable Pulao',
                'category': 'Lunch',
                'diet_type': 'Veg'
            }, follow_redirects=True)
            self.assertEqual(search_res.status_code, 200)
            self.assertIn(b'Fragrant Vegetable Pulao', search_res.data)

            # Verify history page
            hist_res = self.client.get('/history')
            self.assertEqual(hist_res.status_code, 200)
            self.assertIn(b'Vegetable Pulao', hist_res.data)

    def test_06_ai_generation_fallback(self):
        """Test AI search route generates and saves a new dish into recipes table."""
        dish_name = 'Thai Green Curry'
        # Clean up if existed
        execute_db("DELETE FROM recipes WHERE title = %s", (dish_name,))
        
        search_res = self.client.post('/search', data={
            'query': dish_name,
            'category': 'Dinner',
            'diet_type': 'Veg',
            'force_ai': '1'
        }, follow_redirects=True)
        self.assertEqual(search_res.status_code, 200)
        self.assertIn(b'Thai Green Curry', search_res.data)

        # Verify it was persisted to database
        saved = query_db("SELECT * FROM recipes WHERE title = %s", (dish_name,), one=True)
        self.assertIsNotNone(saved)
        self.assertEqual(saved['category'], 'Dinner')

    def test_07_category_filtering(self):
        """Test category filter route."""
        cat_res = self.client.get('/category/Breakfast?diet=Veg')
        self.assertEqual(cat_res.status_code, 200)
        self.assertIn(b'Masala Dosa', cat_res.data)

if __name__ == '__main__':
    unittest.main()
