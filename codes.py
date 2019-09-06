import asyncio


class release:
    def __await__(self):
        yield


async def toto():
    print(1)
    await release()
    print(2)
    await release()
    print(3)


aw = toto()
for v in aw.__await__():
    print('stop', v)


print('---')


async def tata():
    print('a')
    await toto()
    print('b')

aw = tata()
for v in aw.__await__():
    print('stop', v)


print('---')


async def tutu():
    await tata()
    print('c')
    await asyncio.sleep(1)
    print('d')

aw = tutu()
for v in aw.__await__():
    print('stop', v)
    if isinstance(v, asyncio.Future):
        v.set_result(None)
        print('->', v)
