#!/usr/bin/env python3
import asyncio
import logging
import aiohttp


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


parser = etree.HTMLParser()


def is_valid_app_url(url):
    return "https://play.google.com/store/xhr/getdoc?authuser=0"


def make_app_permissions_url():
    pass


def parse_app_permissions(response):
    return etree.parse(io.StringIO(string), parser)


async def parse_app_permissions(url):
    async with ClientSession() as session:
        resp_main_page =  session.get(url)
        if resp_main_page.status_code != 200:
            return None
        resp_app_permissions = session.get()


async def start_client(loop):
    pass


if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    loop.run_until_complete(start_client(loop))

    loop.close()
