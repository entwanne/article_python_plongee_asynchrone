import asyncio


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def simple_print(msg):
    print(msg)


async def complex_work():
    await simple_print('Hello')
    await asyncio.sleep(0)
    await simple_print('World')
