import json
import unittest
import unittest.mock

import api


class TestApi(unittest.TestCase):
    def setUp(self):
        api.app.config['TESTING'] = True
        self.app = api.app.test_client()

    @unittest.mock.patch('api.new_id')
    def test_upload_audiofile_successful(self, new_id):
        new_id.return_value = 'mockid'
        response = self.app.post('/audiofiles/upload', data=b'mock')
        response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(
            {'_links': {'self': {'href': '/audiofiles/mockid'}}}, response
        )


if __name__ == '__main__':
    unittest.main()
