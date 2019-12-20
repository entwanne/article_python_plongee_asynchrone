from contextlib import asynccontextmanager
from codes_3 import aiosocket, Loop


class ARange:
    def __init__(self, stop):
        self.stop = stop

    def __aiter__(self):
        return ARangeIterator(self)


class ARangeIterator:
    def __init__(self, arange):
        self.arange = arange
        self.i = 0

    async def __anext__(self):
        if self.i >= self.arange.stop:
            raise StopAsyncIteration
        await sleep(1)
        i = self.i
        self.i += 1
        return i


async def test_for():
    async for val in ARange(5):
        print(val)


async def arange(stop):
    for i in range(stop):
        await sleep(1)
        yield i


class Server:
    def __init__(self, addr):
        self.socket = aiosocket()
        self.addr = addr

    async def __aenter__(self):
        await self.socket.bind(self.addr)
        await self.socket.listen()
        return self.socket

    async def __aexit__(self, *args):
        self.socket.close()


async def test_with():
    async with Server(('localhost', 8080)) as server:
        with await server.accept() as client:
            msg = await client.recv(1024)
            print('Received from client', msg)
            await client.send(msg[::-1])


@asynccontextmanager
async def server(addr):
    socket = aiosocket()
    try:
        await socket.bind(addr)
        await socket.listen()
        yield socket
    finally:
        socket.close()
