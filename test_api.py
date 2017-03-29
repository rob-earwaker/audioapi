import json
import unittest

import api


class TestApi(unittest.TestCase):
    def setUp(self):
        api.app.config['TESTING'] = True
        self.app = api.app.test_client()

    def test_upload_audiofile(self):
        response = self.app.post('/audiofiles/upload', data=b'mockdata')
        response = json.loads(response.data.decode('utf-8'))
        self.assertIn('self', response['_links'])
        self.assertIn('data', response['_links'])
        self.assertEqual(8, response['length'])

    def test_retrieve_audiofile(self):
        response = self.app.post('/audiofiles/upload', data=b'mockdata')
        response = json.loads(response.data.decode('utf-8'))
        response = self.app.get(response['_links']['self']['href'])
        response = json.loads(response.data.decode('utf-8'))
        self.assertIn('self', response['_links'])
        self.assertIn('data', response['_links'])
        self.assertEqual(8, response['length'])


if __name__ == '__main__':
    unittest.main()
