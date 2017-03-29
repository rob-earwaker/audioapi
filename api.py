import base64
import uuid

import flask


app = flask.Flask(__name__)


store = {}


def new_id():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes)[:-2].decode('ascii')


class AudioFile:
    def __init__(self, id, data):
        self.id = id
        self.data = data

    def length(self):
        return len(self.data)


@app.route('/audiofiles/upload', methods=['POST'])
def upload_audiofile():
    audiofile = AudioFile(new_id(), flask.request.data)
    store[audiofile.id] = audiofile
    return flask.jsonify({
        '_links': {
            'self': {'href': '/audiofiles/{0}'.format(audiofile.id)},
            'data': {'href': '/audiofiles/{0}/data'.format(audiofile.id)}
        },
        'length': audiofile.length()
    })


@app.route('/audiofiles/<id>', methods=['GET'])
def retrieve_audiofile(id):
    audiofile = store[id]
    return flask.jsonify({
        '_links': {
            'self': {'href': '/audiofiles/{0}'.format(audiofile.id)},
            'data': {'href': '/audiofiles/{0}/data'.format(audiofile.id)}
        },
        'length': audiofile.length()
    })


if __name__ == '__main__':
    app.run(debug=True)
