import flask


app = flask.Flask(__name__)


@app.route('/audiofile/upload', methods=['POST'])
def upload_audiofile():
    return flask.request.data


if __name__ == '__main__':
    app.run(debug=True)
