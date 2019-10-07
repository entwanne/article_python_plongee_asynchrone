import asyncio
import time


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def simple_print(msg):
    print(msg)


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


current_loop = None
class Loop:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task.__await__())

    def run(self):
        global current_loop
        current_loop = self
        while self.tasks:
            task = self.tasks.pop(0)
            try:
                next(task)
            except StopIteration:
                pass
            else:
                self.tasks.append(task)

    def run_task(self, task):
        self.add_task(task)
        self.run()


class Waiter:
    def __init__(self, n=1):
        self.i = n

    def set(self):
        self.i -= 1

    def __await__(self):
        while self.i > 0:
            yield


async def gather(*tasks):
    waiter = Waiter(len(tasks))

    async def task_wrapper(task):
        await task
        waiter.set()

    for t in tasks:
        current_loop.add_task(task_wrapper(t))
    await waiter
