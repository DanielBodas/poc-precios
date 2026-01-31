import json
import os
import unittest

class TestMobileConfig(unittest.TestCase):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_package_json_exists(self):
        path = os.path.join(self.BASE_DIR, 'package.json')
        self.assertTrue(os.path.exists(path))
        with open(path, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['name'], 'pricetracker-pro-mobile')
            self.assertIn('@capacitor/core', data['dependencies'])

    def test_capacitor_config_exists(self):
        path = os.path.join(self.BASE_DIR, 'capacitor.config.json')
        self.assertTrue(os.path.exists(path))
        with open(path, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['appId'], 'com.pricetracker.pro')
            self.assertEqual(data['appName'], 'PriceTracker Pro')
            self.assertEqual(data['webDir'], 'www')

    def test_www_config_exists(self):
        path = os.path.join(self.BASE_DIR, 'www', 'config.js')
        self.assertTrue(os.path.exists(path))
        with open(path, 'r') as f:
            content = f.read()
            self.assertIn('window.BACKEND_URL', content)

    def test_api_js_fallback(self):
        path = os.path.join(self.BASE_DIR, 'www', 'js', 'api.js')
        self.assertTrue(os.path.exists(path))
        with open(path, 'r') as f:
            content = f.read()
            # Verify the mobile-specific fallback we added
            self.assertIn('http://localhost:8000', content)

if __name__ == '__main__':
    unittest.main()
