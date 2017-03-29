import io
import json
import unittest

import api


class TestApi(unittest.TestCase):
    def setUp(self):
        api.app.config['TESTING'] = True
        self.app = api.app.test_client()

    def test_upload_audiofile(self):
        response = self.app.post(
            '/audiofiles/upload',
            content_type='multipart/form-data',
            data={'file': (io.BytesIO(b'mockdata'), 'mockname.bin')}
        )
        response = json.loads(response.data.decode('utf-8'))
        self.assertIn('self', response['_links'])
        self.assertIn('data', response['_links'])
        self.assertEqual('mockname.bin', response['name'])
        self.assertEqual(8, response['length'])

    def test_retrieve_audiofile(self):
        response = self.app.post(
            '/audiofiles/upload',
            content_type='multipart/form-data',
            data={'file': (io.BytesIO(b'mockdata'), 'mockname.bin')}
        )
        response = json.loads(response.data.decode('utf-8'))
        response = self.app.get(response['_links']['self']['href'])
        response = json.loads(response.data.decode('utf-8'))
        self.assertIn('self', response['_links'])
        self.assertIn('data', response['_links'])
        self.assertEqual('mockname.bin', response['name'])
        self.assertEqual(8, response['length'])

    def test_retrieve_audiofile_data(self):
        response = self.app.post(
            '/audiofiles/upload',
            content_type='multipart/form-data',
            data={'file': (io.BytesIO(b'mockdata'), 'mockname.bin')}
        )
        response = json.loads(response.data.decode('utf-8'))
        response = self.app.get(response['_links']['data']['href'])
        self.assertEqual(b'mockdata', response.data)


if __name__ == '__main__':
    unittest.main()
