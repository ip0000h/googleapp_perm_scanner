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
    parsed_url_data = urlparse(url)
    parsed_qs = parse_qs(parsed_url_data.query)
    if parsed_url_data.netloc != GOOGLE_DOMAIN or parsed_qs.get('hl')[0] not in ALLOWED_LANGS:
        return web.HTTPNotFound()
    search_id = "{}_{}".format(parsed_qs.get('id')[0], parsed_qs.get('hl')[0])
    exist_data = await db.permissions.find_one(
        {'id': search_id}
    )
    if exist_data:
        exist_data.pop('_id')
        exist_data.pop('id')
        return web.json_response(exist_data, status=200)
    permissions_in_data = {
        'id': parsed_qs.get('id')[0],
        'hl': parsed_qs.get('hl')[0]
    }
    permissions_in_exist = await db.permissions_in.find_one(
        permissions_in_data
    )
    if not permissions_in_exist:
        await db.permissions_in.insert_one(permissions_in_data)
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
