import unittest

import api


class TestApi(unittest.TestCase):
    def setUp(self):
        api.app.config['TESTING'] = True
        self.app = api.app.test_client()

    def test_root(self):
        self.assertEqual(b'Hello, World!', self.app.get('/').data)


if __name__ == '__main__':
    unittest.main()
