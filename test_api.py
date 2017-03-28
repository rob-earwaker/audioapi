import unittest

import api


class TestApi(unittest.TestCase):
    def setUp(self):
        api.app.config['TESTING'] = True
        self.app = api.app.test_client()

    def test_root(self):
        response = self.app.post('/audiofile/upload', data='Hello, World!')
        self.assertEqual(b'Hello, World!', response.data)


if __name__ == '__main__':
    unittest.main()
