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
            '/audiofiles',
            content_type='multipart/form-data',
            data={'file': (io.BytesIO(b'mockdata'), 'mockname.bin')}
        )
        response = json.loads(response.data.decode('utf-8'))
        self.assertIn('self', response['_links'])
        self.assertIn('data', response['_links'])
        self.assertIn('audiofiles', response['_links'])
        self.assertEqual('mockname.bin', response['name'])
        self.assertEqual(8, response['length'])

    def test_retrieve_audiofile(self):
        response = self.app.post(
            '/audiofiles',
            content_type='multipart/form-data',
            data={'file': (io.BytesIO(b'mockdata'), 'mockname.bin')}
        )
        response = json.loads(response.data.decode('utf-8'))
        response = self.app.get(response['_links']['self']['href'])
        response = json.loads(response.data.decode('utf-8'))
        self.assertIn('self', response['_links'])
        self.assertIn('data', response['_links'])
        self.assertIn('audiofiles', response['_links'])
        self.assertEqual('mockname.bin', response['name'])
        self.assertEqual(8, response['length'])

    def test_retrieve_audiofile_data(self):
        response = self.app.post(
            '/audiofiles',
            content_type='multipart/form-data',
            data={'file': (io.BytesIO(b'mockdata'), 'mockname.bin')}
        )
        response = json.loads(response.data.decode('utf-8'))
        response = self.app.get(response['_links']['data']['href'])
        self.assertEqual(b'mockdata', response.data)

    def test_list_audiofiles(self):
        response = self.app.get('/audiofiles')
        response = json.loads(response.data.decode('utf-8'))
        response = self.app.post(
            response['_links']['upload']['href'],
            content_type='multipart/form-data',
            data={'file': (io.BytesIO(b'mockdata1'), 'mockname1.bin')}
        )
        response = json.loads(response.data.decode('utf-8'))
        response = self.app.get(response['_links']['audiofiles']['href'])
        response = json.loads(response.data.decode('utf-8'))
        response = self.app.post(
            response['_links']['upload']['href'],
            content_type='multipart/form-data',
            data={'file': (io.BytesIO(b'mockdata2'), 'mockname2.bin')}
        )
        response = json.loads(response.data.decode('utf-8'))
        response = self.app.get(response['_links']['audiofiles']['href'])
        response = json.loads(response.data.decode('utf-8'))
        self.assertIn('self', response['_links'])
        self.assertIn('upload', response['_links'])
        self.assertEqual(2, response['count'])
        self.assertEqual(2, len(response['_embedded']['audiofile']))
        audiofile1 = next(
            audiofile for audiofile in response['_embedded']['audiofile']
            if audiofile['name'] == 'mockname1.bin'
        )
        self.assertIn('self', audiofile1['_links'])
        self.assertIn('data', audiofile1['_links'])
        self.assertEqual(9, audiofile1['length'])
        audiofile2 = next(
            audiofile for audiofile in response['_embedded']['audiofile']
            if audiofile['name'] == 'mockname2.bin'
        )
        self.assertIn('self', audiofile2['_links'])
        self.assertIn('data', audiofile2['_links'])
        self.assertEqual(9, audiofile2['length'])


if __name__ == '__main__':
    unittest.main()
