import asyncio
import uuid
from functools import partial

import aiohttp


class Wallet:
    def __init__(self, url: str, rpc_user: str, rpc_password: str, *args, **kwargs):
        self.session = aiohttp.ClientSession(auth=aiohttp.BasicAuth(rpc_user, rpc_password))
        self.url = url

    def close(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.session.close())

    def __del__(self):
        self.close()

    def __getattr__(self, item):
        return partial(call, session=self.session, url=self.url, method=item)


async def call(*args, session: aiohttp.ClientSession, url: str, method: str):
    _id = str(uuid.uuid4())
    async with session.post(url, json={'jsonrpc':'2.0', 'method': method, 'params':args, 'id': _id}) as resp:
        response = await resp.json()
        assert response['id'] == _id

        if 'error' in response and response['error']:
            raise Exception(response['error'])

        return response['result']
