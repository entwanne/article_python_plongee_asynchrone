import select
import socket
import time


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


class Loop:
    current = None

    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        if hasattr(task, '__await__'):
            task = task.__await__()
        self.tasks.append(task)

    def run(self):
        Loop.current = self
        while self.tasks:
            task = self.tasks.pop(0)
            try:
                next(task)
            except StopIteration:
                pass
            else:
                self.add_task(task)

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
        Loop.current.add_task(task_wrapper(t))
    await waiter


class AIOSocket:
    def __init__(self, socket):
        self.socket = socket
        self.pollin = select.epoll()
        self.pollin.register(self, select.EPOLLIN)
        self.pollout = select.epoll()
        self.pollout.register(self, select.EPOLLOUT)

    def close(self):
        self.socket.close()

    def fileno(self):
        return self.socket.fileno()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.socket.close()

    async def bind(self, addr):
        while not self.pollin.poll():
            await interrupt()
        self.socket.bind(addr)

    async def listen(self):
        while not self.pollin.poll():
            await interrupt()
        self.socket.listen()

    async def connect(self, addr):
        while not self.pollin.poll():
            await interrupt()
        self.socket.connect(addr)

    async def accept(self):
        while not self.pollin.poll(0):
            await interrupt()
        client, _ = self.socket.accept()
        return self.__class__(client)

    async def recv(self, bufsize):
        while not self.pollin.poll(0):
            await interrupt()
        return self.socket.recv(bufsize)

    async def send(self, bytes):
        while not self.pollout.poll(0):
            await interrupt()
        return self.socket.send(bytes)


def aiosocket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None):
    return AIOSocket(socket.socket(family, type, proto, fileno))


async def server_coro():
    with aiosocket() as server:
        await server.bind(('localhost', 8080))
        await server.listen()
        with await server.accept() as client:
            msg = await client.recv(1024)
            print('Received from client', msg)
            await client.send(msg[::-1])


async def client_coro():
    with aiosocket() as client:
        await client.connect(('localhost', 8080))
        await client.send(b'Hello World!')
        msg = await client.recv(1024)
        print('Received from server', msg)
