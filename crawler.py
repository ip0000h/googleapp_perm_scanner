#!/usr/bin/env python3
import asyncio
import json
import logging
import os
import re
from contextlib import suppress
from datetime import datetime

from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

PERMISSIONS_URL = 'https://play.google.com/_/PlayStoreUi/data/batchexecute'
DEFAULT_PARAMS = {
    'rpcids': 'xdSrCf',
    'f.sid': '5600643832700570820',
    'bl': 'boq_playuiserver_20190421.14_p0',
    'authuser': '',
    'soc-app': '121',
    'soc-platform': '1',
    'soc-device': '1',
    '_reqid': '329479',
    'rt': 'c',
}
OTHER_EXTENSIONS_EN_NAME = 'Other'
OTHER_EXTENSIONS_RU_NAME = 'Другое'

client = AsyncIOMotorClient('mongo')
db = client.google_permissions_parser


async def get_app_permissions_data(app_id, language):
    """
    Возвращает данные по разрешениям в формате ответа от google apps
    по app_id и language
    В случае ошибки - возвращает None
    """
    params = dict(DEFAULT_PARAMS)
    params['hl'] = language
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
        logger.debug('Response status: %s' % resp_app_permissions.status)
        logger.debug('Response headers: %s' % resp_app_permissions.headers)
        logger.debug('Response cookies: %s' % resp_app_permissions.cookies)
        if resp_app_permissions.status != 200:
            return None
        resp_app_permissions_text = await resp_app_permissions.text()
        logger.debug('Response text: %s' % resp_app_permissions_text)
        return resp_app_permissions_text


async def save_permission_icon(url):
    """
    Сохраняем данные об иконке в статику, возвращаем имя файла
    """
    filename = '{0}.png'.format(url.rsplit('/', maxsplit=1)[1])
    if not os.path.exists('static'):
        os.makedirs('static')
    path = os.path.join('static', filename)
    async with ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
    with open(path, 'wb') as icon_file:
        icon_file.write(data)
    return filename


async def save_permission(data):
    """
    Сохраняем полученные данные в БД
    """
    return await db.permissions.insert_one(data)


async def parse_app_permissions_data(raw_data, language):
    """
    Парсит данные, полученные от google apps в json format
    В случае ошибки - возвращает None
    """
    res = {}
    data = re.findall(r'\"(\[.*\\n)\"', raw_data)
    if not data or not isinstance(data, list) or not len(data) == 1:
        print('Wrong data format: %s' % data)
        return None
    data = data[0].replace('\\n', '').replace('\\', '')
    data = json.loads(data)
    if not data or not isinstance(data, list):
        print('Wrong data format: %s' % data)
        return None
    main_permissions = data[0]
    if not main_permissions:
        main_permissions = []
    other_permissions = data[1:]
    for perm_block in main_permissions + other_permissions[0]:
        if not perm_block or not isinstance(perm_block, list):
            continue
        block_name = perm_block[0]
        icon_url = perm_block[1][3][2]
        icon_filename = await save_permission_icon(icon_url)
        permissions = [perm[1] for perm in perm_block[2]]
        if not block_name in res:
            res[block_name] = {
                'icon': icon_filename,
                'permissions': permissions
            }
        else:
            res[block_name]['permissions'].extend(permissions)
    if len(data) == 3 and other_permissions[1]:
        for perm in other_permissions[1]:
            if language == 'en':
                res[OTHER_EXTENSIONS_EN_NAME]['permissions'].append(perm[1])
            else:
                res[OTHER_EXTENSIONS_RU_NAME]['permissions'].append(perm[1])
    return res


async def set_error(doc_id):
    await db.permissions_in.update_one({'_id': doc_id}, {"$set": {'error': True}})


async def set_success(doc_id):
    await db.permissions_in.update_one({'_id': doc_id}, {"$set":{'error': False}})


async def start_client(loop):
    while True:
        async for application in db.permissions_in.find({'error': {'$exists': False}}):
            doc_id = application.get('_id')
            app_id = application.get('id')
            language = application.get('hl')
            data = await get_app_permissions_data(app_id, language)
            if not data:
                print("No application data app_id: %s language: %s" % (app_id, language))
                await set_error(doc_id)
                continue
            parsed_data = await parse_app_permissions_data(data, language)
            if not parsed_data:
                print("Cannot parse data app_id: %s language: %s data: %s" % (app_id, language, data))
                await set_error(doc_id)
                continue
            parsed_data['id'] = "{}_{}".format(app_id, language)
            await save_permission(parsed_data)
            await set_success(doc_id)
        await asyncio.sleep(1)

# async def watch(collection):
#     async with collection.watch([]) as stream:
#         async for change in stream:
#             print(change)


# async def cleanup(task):
#     task.cancel()
#     with suppress(asyncio.CancelledError):
#         await task


if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    # task = asyncio.ensure_future(watch(db.permissions_in))

    try:
        loop.run_until_complete(start_client(loop))
        # loop.run_forever()
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        # loop.run_until_complete(cleanup(task))
        # loop.run_until_complete(asyncio.sleep(client.server_selection_timeout))

        # loop.shutdown_asyncgens()
        loop.close()
