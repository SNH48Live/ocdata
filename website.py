#!/usr/bin/env python3

import html
import json
import math
import mimetypes
import os

import arrow
import attrdict
import flask

from lib.config import INDEX, METADATA_DIR, PLOTS_DIR, TRANSCRIPTS_DIR
from lib.emojis import EMOJI_MAXLEN, EMOJI_TRIE


app = flask.Flask(__name__)
PER_PAGE = 12
streams = None
streams_index = None


def load_streams():
    global streams
    global streams_index
    streams = []
    streams_index = {}
    with open(INDEX) as fp:
        for line in fp:
            date, video_id = line.split()
            metadata_file = METADATA_DIR / f'{date}-{video_id}.json'
            with open(metadata_file) as fmeta:
                stream = attrdict.AttrDict(json.load(fmeta))
                streams.append(stream)
                streams_index[video_id] = stream
    streams = list(reversed(streams))


load_streams()


# Credit: http://flask.pocoo.org/snippets/44/
class Pagination(object):

    def __init__(self, page, per_page, total):
        self.page = page
        self.per_page = per_page
        self.total = total

    @property
    def pages(self):
        return int(math.ceil(self.total / self.per_page))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    # Refer to http://flask-sqlalchemy.pocoo.org/2.3/api/#flask_sqlalchemy.Pagination
    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if ((num <= left_edge or num > self.pages - right_edge or
                 (num > self.page - left_current - 1 and num < self.page + right_current))):
                if last + 1 != num:
                    yield None
                yield num
                last = num


def get_transcript(video_id, suffix):
    path = TRANSCRIPTS_DIR.joinpath(video_id).with_suffix(suffix)
    if path.exists():
        return os.fspath(path)
    else:
        flask.abort(404)


@app.template_filter('formatdatetime')
def formatdatetime(datetime_):
    return arrow.get(datetime_).to('Asia/Shanghai').strftime('%Y-%m-%d %H:%M:%S')


@app.template_filter('formatoffset')
def formatoffset(offset):
    seconds = int(offset % 60)
    minutes = int(offset / 60) % 60
    hours = int(offset / 3600)
    return f'{hours:01d}:{minutes:02d}:{seconds:02d}'


def emojipath(emoji):
    html_entity = ''.join(f'&#x{ord(char):x}' for char in emoji)
    filename = 'emoji_u' + '_'.join(f'{ord(char):x}' for char in emoji) + '.svg'
    return flask.url_for('static', filename=f'emojis/{filename}')


# The returned string is HTML-safe.
@app.template_filter('markupemojis')
def markupemojis(text):
    result = ''
    while text:
        # Find out whether an emoji starts at the current position.
        emoji = EMOJI_TRIE.longest_prefix(text[:EMOJI_MAXLEN])[0]
        if not emoji:
            result += html.escape(text[0])
            text = text[1:]
        else:
            result += f'<img class="emoji" height="24" width="24" alt="{emoji}" src="{emojipath(emoji)}">'
            text = text[len(emoji):]
    return result


# We use an optional argument page here instead of the standard
#
#     @app.route('/', defaults=dict(page=1))
#     @app.route('/<int:page>/')
#     def index(page):
#
# because otherwise Frozen-Flask would refuse to generate /1/.
@app.route('/')
@app.route('/<int:page>/')
def index(page=1):
    pagination = Pagination(page, PER_PAGE, len(streams))
    return flask.render_template('index.html',
                                 pagination=pagination,
                                 streams=streams[(page - 1) * PER_PAGE : page * PER_PAGE])


@app.route('/stats/<video_id>.html')
def stream_stats(video_id):
    if video_id in streams_index:
        return flask.render_template('stream.html', stream=streams_index[video_id])
    else:
        flask.abort(404)


@app.route('/plot/<filename>')
def plot(filename):
    path = PLOTS_DIR / filename
    mimetype, _ = mimetypes.guess_type(path.name)
    if path.exists():
        return flask.send_file(os.fspath(path), mimetype=mimetype)
    else:
        flask.abort(404)


@app.route('/transcript/<video_id>.txt')
def transcript_txt(video_id):
    return flask.send_file(get_transcript(video_id, '.txt'), mimetype='text/plain')


@app.route('/transcript/<video_id>.json')
def transcript_json(video_id):
    return flask.send_file(get_transcript(video_id, '.json'), mimetype='application/json')


@app.route('/transcript/<video_id>.html')
def transcript_html(video_id):
    messages = []
    with open(get_transcript(video_id, '.json')) as fp:
        for line in fp:
            messages.append(attrdict.AttrDict(json.loads(line)))
    return flask.render_template('transcript.html', video_id=video_id, messages=messages)


@app.errorhandler(404)
def not_found(e):
    return flask.render_template('404.html'), 404


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.run(debug=True)
