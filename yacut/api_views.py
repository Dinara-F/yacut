from flask import jsonify, request
from string import ascii_letters, digits
from http import HTTPStatus

from . import app, db
from .models import URL_map
from .views import get_unique_short_id
from .error_handlers import InvalidAPIUsage


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_original(short_id):
    url = URL_map.query.filter_by(short=short_id).first()
    if url is None:
        return (jsonify({'message': 'Указанный id не найден'}),
                HTTPStatus.NOT_FOUND)
    original = url.original
    return jsonify({'url': original}), HTTPStatus.OK


@app.route('/api/id/', methods=['POST'])
def add_url():
    data = request.get_json()
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data or data['url'] == '' or data['url'] is None:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    if (
        'custom_id' not in data or
        data['custom_id'] is None or data['custom_id'] == ''
    ):
        data['custom_id'] = get_unique_short_id()
    if len(data['custom_id']) > 16:
        raise InvalidAPIUsage('Указано недопустимое имя для короткой ссылки')
    if set(data['custom_id']).difference(ascii_letters + digits):
        raise InvalidAPIUsage('Указано недопустимое имя для короткой ссылки')
    if URL_map.query.filter_by(short=data['custom_id']).first() is not None:
        short = data['custom_id']
        raise InvalidAPIUsage(f'Имя "{short}" уже занято.')
    url = URL_map()
    url.from_dict(data)
    db.session.add(url)
    db.session.commit()
    return jsonify(url.to_dict()), HTTPStatus.CREATED