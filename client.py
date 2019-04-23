#!/usr/bin/env python3
import asyncio
import io
import logging
from aiohttp import web, ClientSession
from lxml import etree


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def index(request):
    return web.FileResponse('./templates/index.html')


# async def static(reuest):
#     return web.FileResponse('./static/{}'.format())


async def new_application(request):
    data_json = await request.post()
    url = data_json.get('url')
    print(url)
    data = await parse_app_page(url)
    data = [
        {
            'name': 'Identity',
            'icon': 'file_icon_name',
            'permissions': [
                'find accounts on the device',
                'add or remove accounts',
                'read your own contact card'
            ]
        },
        {
            'name': 'Contacts',
            'icon': 'file_icon_name',
            'permissions': [
                'find accounts on the device',
                'read your contacts',
                'modify your contacts'
            ]
        },
    ]
    return web.json_response(data)


if __name__ == '__main__':
    app = web.Application()
    app.add_routes(
        [
            web.get('/', index),
            # web.post('/static/', static),
            web.post('/api/application/new', new_application)
        ]
    )

    web.run_app(app)
