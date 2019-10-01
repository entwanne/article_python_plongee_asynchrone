import asyncio
import time


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def simple_print(msg):
    print(msg)


def run_tasks(*tasks):
    tasks = [task.__await__() for task in tasks]

    while tasks:
        # On prend la première tâche disponible
        task = tasks.pop(0)
        try:
            next(task)
        except StopIteration:
            # La tâche est terminée
            pass
        else:
            # La tâche continue, on la remet en queue de liste
            tasks.append(task)


async def complex_work():
    await simple_print('Hello')
    await asyncio.sleep(0)
    await simple_print('World')


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


def run_task(task):
    it = task.__await__()

    while True:
        try:
            next(it)
        except StopIteration:
            break


def run_tasks(*tasks):
    tasks = [task.__await__() for task in tasks]

    while tasks:
        # On prend la première tâche disponible
        task = tasks.pop(0)
        try:
            next(task)
        except StopIteration:
            # La tâche est terminée
            pass
        else:
            # La tâche continue, on la remet en queue de liste
            tasks.append(task)


class interrupt:
    def __await__(self):
        yield


async def sleep_until(t):
    while time.time() < t:
        await interrupt()


async def sleep(duration):
    await sleep_until(time.time() + duration)


async def print_messages(*messages, sleep_time=1):
    for msg in messages:
        print(msg)
        await sleep(sleep_time)
