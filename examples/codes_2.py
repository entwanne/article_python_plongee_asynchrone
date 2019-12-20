import asyncio


class ComplexWork:
    def __await__(self):
        print('Hello')
        yield
        print('World')


class Waiter:
    def __init__(self):
        self.done = False

    def __await__(self):
        while not self.done:
            yield


async def wait_job(waiter):
    print('start')
    await waiter
    print('finished')


async def count_up_to(waiter, n):
    for i in range(n):
        print(i)
        await asyncio.sleep(0)
    waiter.done = True
