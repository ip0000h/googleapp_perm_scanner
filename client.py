#!/usr/bin/env python3
import logging
import os
from urllib.parse import parse_qs, urlparse


from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

GOOGLE_DOMAIN = 'play.google.com'
ALLOWED_LANGS = ['en', 'ru']

client = AsyncIOMotorClient('mongo')
db = client.google_permissions_parser


async def index(request):
    return web.FileResponse('./templates/index.html')


async def new_application(request):
    data_json = await request.post()
    url = data_json.get('url')

    if not url.startswith('https://'):
        app_id = url
        language = ALLOWED_LANGS[0]
    else:
        parsed_url_data = urlparse(url)
        parsed_qs = parse_qs(parsed_url_data.query)
        if parsed_url_data.netloc != GOOGLE_DOMAIN:
            print('Wrong domain in url %s' % url)
            return web.HTTPNotFound()
        if parsed_qs.get('hl') and parsed_qs.get('hl')[0] not in ALLOWED_LANGS:
            print('Wrong language in url %s' % url)
            return web.HTTPNotFound()
        app_id = parsed_qs.get('id')[0]
        if not parsed_qs.get('hl'):
            language = ALLOWED_LANGS[0]
        else:
            language = parsed_qs.get('hl')[0]

    print("Searching app_id: %s language: %s" % (app_id, language))
    search_id = "{}_{}".format(app_id, language)

    exist_data = await db.permissions.find_one(
        {'id': search_id}
    )
    if exist_data:
        exist_data.pop('_id')
        exist_data.pop('id')
        return web.json_response(exist_data, status=200)

    permissions_in_data = {
        'id': app_id,
        'hl': language
    }
    permissions_in_exist = await db.permissions_in.find_one(
        permissions_in_data
    )
    if not permissions_in_exist:
        await db.permissions_in.insert_one(permissions_in_data)
    elif 'error' in permissions_in_exist:
        print('Wrong request for %s' % url)
        return web.HTTPNotFound()
    return web.json_response({}, status=202)


if __name__ == '__main__':
    app = web.Application()
    app.add_routes(
        [
            web.get('/', index),
            web.post('/api/application/new', new_application)
        ]
    )
    if not os.path.exists('static'):
        os.makedirs('static')
    app.router.add_static('/static/', path='./static/', name='static')

    web.run_app(app)
