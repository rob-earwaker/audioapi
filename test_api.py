import json
import unittest

import api


class TestApi(unittest.TestCase):
    def setUp(self):
        api.app.config['TESTING'] = True
        self.app = api.app.test_client()

    def test_retrieve_audiofile_after_upload(self):
        response = self.app.post('/audiofiles/upload', data=b'mockdata')
        response = json.loads(response.data.decode('utf-8'))
        response = self.app.get(response['_links']['self']['href'])
        self.assertEqual(b'mockdata', response.data)


if __name__ == '__main__':
    unittest.main()
