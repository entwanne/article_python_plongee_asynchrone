import heapq
import time
from functools import total_ordering


class Future:
    def __init__(self):
        self._done = False
        self.task = None

    def __await__(self):
        yield self
        assert self._done

    def set(self):
        self._done = True
        if self.task is not None:
            Loop.current.add_task(self.task)


class Loop:
    current = None

    def __init__(self):
        self.tasks = []
        self.handlers = []

    def add_task(self, task):
        if hasattr(task, '__await__'):
            task = task.__await__()
        self.tasks.append(task)

    def run(self):
        Loop.current = self
        while self.tasks or self.handlers:
            if self.handlers and self.handlers[0].t <= time.time():
                handler = heapq.heappop(self.handlers)
                handler.future.set()

            if not self.tasks:
                continue
            task = self.tasks.pop(0)
            try:
                result = next(task)
            except StopIteration:
                continue

            if isinstance(result, Future):
                result.task = task
            else:
                self.tasks.append(task)

    def run_task(self, task):
        self.add_task(task)
        self.run()

    def call_later(self, t, future):
        heapq.heappush(self.handlers, TimeEvent(t, future))


@total_ordering
class TimeEvent:
    def __init__(self, t, future):
        self.t = t
        self.future = future

    def __eq__(self, rhs):
        return self.t == rhs.t

    def __lt__(self, rhs):
        return self.t < rhs


async def sleep(t):
    future = Future()
    Loop.current.call_later(time.time() + t, future)
    await future
