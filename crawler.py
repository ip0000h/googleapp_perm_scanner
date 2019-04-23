#!/usr/bin/env python3
import asyncio
import json
import logging
import re
from datetime import datetime

from aiohttp import ClientSession, CookieJar


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

PERMISSIONS_URL = 'https://play.google.com/_/PlayStoreUi/data/batchexecute'


async def get_app_permissions_data(app_id, language):
    """
    Возвращает данные по разрешениям
    """
    params = {
        'rpcids': 'xdSrCf',
        'f.sid': '5600643832700570820',
        'bl': 'boq_playuiserver_20190421.14_p0',
        'hl': language,
        'authuser': '',
        'soc-app': '121',
        'soc-platform': '1',
        'soc-device': '1',
        '_reqid': '329479',
        'rt': 'c',
    }
    async with ClientSession() as session:
        data = {
            'f.req': r'[[["xdSrCf","[[null,[\"{}\",7],[]]]",null,"IZBjA:0|mC"]]]'.format(app_id),
            '': '',
        }
        resp_app_permissions = await session.post(
            PERMISSIONS_URL,
            params=params,
            data=data
        )
        print('Response status: %s' % resp_app_permissions.status)
        print('Response headers: %s' % resp_app_permissions.headers)
        print('Response cookies: %s' % resp_app_permissions.cookies)
        if resp_app_permissions.status != 200:
            return None
        resp_app_permissions_text = await resp_app_permissions.text()
        print('Response text: %s' % resp_app_permissions_text)
        return resp_app_permissions_text


async def start_client(loop):
    pass


if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    loop.run_until_complete(start_client(loop))

    loop.close()
