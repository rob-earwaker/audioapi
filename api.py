import base64
import io
import uuid

import flask

import wav


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

    @staticmethod
    def href(id):
        return '/audiofiles/{0}'.format(id)

    def document(self):
        return {
            '_links': {
                'self': {'href': self.href(self.id)},
                'audiodata': {'href': AudioData.href(self.id)},
                'audiofiles': {'href': AudioFiles.href()}
            },
            'name': self.name,
            'length': self.length()
        }

    def embedded(self):
        return {
            '_links': {
                'self': {'href': self.href(self.id)}
            },
            'name': self.name,
            'length': self.length()
        }


class AudioFiles:
    def __init__(self, audiofiles):
        self.audiofiles = audiofiles

    def count(self):
        return len(self.audiofiles)

    @staticmethod
    def href():
        return '/audiofiles'

    def document(self):
        return {
            '_links': {
                'self': {'href': self.href()},
                'upload': {'href': self.href()}
            },
            'count': self.count(),
            '_embedded': {
                'audiofile': [
                    audiofile.embedded() for audiofile in self.audiofiles
                ]
            }
        }


@app.route(AudioFiles.href(), methods=['GET'])
def list_audiofiles():
    audiofiles = AudioFiles(store.values())
    return flask.jsonify(audiofiles.document())


@app.route(AudioFiles.href(), methods=['POST'])
def upload_audiofile():
    file = flask.request.files['file']
    audiofile = AudioFile(new_id(), file.filename, file.read())
    store[audiofile.id] = audiofile
    return flask.jsonify(audiofile.document())


@app.route(AudioFile.href('<id>'), methods=['GET'])
def retrieve_audiofile(id):
    mimetype = flask.request.accept_mimetypes.best
    audiofile = store[id]
    if mimetype == 'application/octet-stream':
        return audiofile.data
    else:
        return flask.jsonify(audiofile.document())


class AudioData:
    def __init__(self, id, samplerate, channels, bitspersample):
        self.id = id
        self.samplerate = samplerate
        self.channels = channels
        self.bitspersample = bitspersample

    @staticmethod
    def href(id):
        return '{0}/data'.format(AudioFile.href(id))

    def document(self):
        return {
            '_links': {
                'self': {'href': self.href(self.id)},
                'audiofile': {'href': AudioFile.href(self.id)},
                'audiofiles': {'href': AudioFiles.href()}
            },
            'samplerate': self.samplerate,
            'channels': self.channels,
            'bitsPerSample': self.bitspersample
        }


@app.route(AudioData.href('<id>'), methods=['GET'])
def retrieve_audiodata(id):
    audiofile = store[id]
    wavfile = wav.read(io.BytesIO(audiofile.data))
    audiodata = AudioData(
        id, wavfile.sample_rate, wavfile.channel_count, wavfile.bits_per_sample
    )
    return flask.jsonify(audiodata.document())


if __name__ == '__main__':
    app.run(debug=True)
