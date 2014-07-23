import os
import random
import string
import time
from urlparse import urlparse

from flask import Flask, request, make_response, abort
from flask.json import jsonify

EXPIRATION_TIME_SECONDS = 300

# File store
FILES_DIR = 'geogists/'

# Characters to use for generating filenames
CHARS = string.ascii_uppercase + string.ascii_lowercase + string.digits

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  # Max file size is 30 MB

if not os.path.exists(FILES_DIR):
    os.mkdir(FILES_DIR)

@app.route('/api/v0/geogist', methods=['POST'])
def create_geogist():
    _remove_expired_files()

    data = request.form.keys()[0]
    gistid = _generate_gistid()
    with open(_filename_from_gistid(gistid), 'w') as f:
        f.write(data)

    return jsonify(id=gistid)


@app.route('/api/v0/geogist/<gistid>')
def get_geogist(gistid):
    _remove_expired_files()

    filename = _filename_from_gistid(gistid)
    try:
        with open(filename) as f:
            data = f.read()
        os.remove(filename)
    except IOError:
        abort(404)

    resp = make_response(data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


def _generate_gistid(n=20):
    gistid = None
    while gistid is None or os.path.exists(_filename_from_gistid(gistid)):
        gistid = ''.join(random.choice(CHARS) for x in range(n)) + '.geojson'
    return gistid


def _filename_from_gistid(gistid):
    return os.path.join(FILES_DIR, gistid)


def _remove_expired_files():
    files = os.listdir(FILES_DIR)
    t = time.time()
    for f in files:
        filename = os.path.join(FILES_DIR, f)
        # Put everything in a try/except block as another thread could delete
        # a file before this one has the chance to do it
        try:
            t_creation = os.path.getctime(filename)
            if t - t_creation > EXPIRATION_TIME_SECONDS:
                os.remove(filename)
        except:
            pass


if __name__ == '__main__':
    app.run()
