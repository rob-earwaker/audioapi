import base64
import uuid

import flask


app = flask.Flask(__name__)


store = {}


def new_id():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes)[:-2].decode('ascii')


class AudioFile:
    def __init__(self, id, name, data):
        self.id = id
        self.name = name
        self.data = data

    def length(self):
        return len(self.data)


@app.route('/audiofiles', methods=['GET'])
def list_audiofiles():
    audiofiles = store.values()
    return flask.jsonify({
        '_links': {
            'self': {'href': '/audiofiles'},
            'upload': {'href': '/audiofiles/upload'}
        },
        'count': len(audiofiles),
        '_embedded': {
            'audiofile': [
                {
                    '_links': {
                        'self': {
                            'href': '/audiofiles/{0}'.format(audiofile.id)
                        },
                        'data': {
                            'href': '/audiofiles/{0}/data'.format(audiofile.id)
                        }
                    },
                    'name': audiofile.name,
                    'length': audiofile.length()
                }
                for audiofile in audiofiles
            ]
        }
    })


@app.route('/audiofiles/upload', methods=['POST'])
def upload_audiofile():
    file = flask.request.files['file']
    audiofile = AudioFile(new_id(), file.filename, file.read())
    store[audiofile.id] = audiofile
    return flask.jsonify({
        '_links': {
            'self': {'href': '/audiofiles/{0}'.format(audiofile.id)},
            'data': {'href': '/audiofiles/{0}/data'.format(audiofile.id)},
            'audiofiles': {'href': '/audiofiles'}
        },
        'name': audiofile.name,
        'length': audiofile.length()
    })


@app.route('/audiofiles/<id>', methods=['GET'])
def retrieve_audiofile(id):
    audiofile = store[id]
    return flask.jsonify({
        '_links': {
            'self': {'href': '/audiofiles/{0}'.format(audiofile.id)},
            'data': {'href': '/audiofiles/{0}/data'.format(audiofile.id)},
            'audiofiles': {'href': '/audiofiles'}
        },
        'name': audiofile.name,
        'length': audiofile.length()
    })


@app.route('/audiofiles/<id>/data', methods=['GET'])
def retrieve_audiofile_data(id):
    audiofile = store[id]
    return audiofile.data


if __name__ == '__main__':
    app.run(debug=True)
