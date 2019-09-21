On a vu que les coroutines pouvaient s'utiliser dans des boucles événementielles ou derrière le mot-clé *await*, mais d'autres objets en sont aussi capables.
On parle ainsi plus généralement de tâches asynchrones ou d'*awaitables*.

Un *awaitable* est un objet qui possède une méthode spéciale `__await__`, renvoyant un itérateur.

Voici par exemple un équivalent de notre fonction `complex_work`.

```python
class ComplexWork:
    def __await__(self):
        print('Hello')
        yield
        print('World')
```

Avec le mot-clé `yield`, notre méthode `__await__` devient une fonction génératrice et renvoie donc un itérateur.

Nous pouvons exécuter notre tâche asynchrone dans une boucle évenementielle `asyncio` :

```python
>>> loop.run_until_complete(ComplexWork())
Hello
World
```

Ou via une itération manuelle comme précédemment :

```python
>>> it = ComplexWork().__await__()
>>> next(it)
Hello
>>> next(it)
World
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

Les exemples montrent ici une utilisation directe de notre tâche, mais nous pourrions tout aussi bien l'utiliser derrière un `await`.

```python
>>> async def runner():
...     await ComplexWork()
... 
>>> loop.run_until_complete(runner())
Hello
World
```

Il est peu fréquent d'avoir à définir un *awaitable* autre qu'une coroutine, mais cela peut être utile pour toucher aux aspects bas-niveau du moteur asynchrone ou pour associer un état à notre tâche.

```python
class Waiter:
    def __init__(self):
        self.done = False

    def __await__(self):
        while not self.done:
            yield
```

```python
>>> waiter = Waiter()
>>>
>>> async def coro1():
...     print('start')
...     await waiter
...     print('finished')
...
>>> async def coro2():
...     for i in range(10):
...         print(i)
...         await asyncio.sleep(1)
...     waiter.done = True
...
>>> loop.run_until_complete(asyncio.gather(coro1(), coro2()))
start
0
1
2
3
4
5
6
7
8
9
finished
[None, None]
```

(`gather` est un utilitaire `asyncio` pour exécuter simultanément plusieurs tâches).

Comme on le voit, notre objet `Waiter` permet à `coro1` d'attendre la fin de l'exécution de `coro2` avant de continuer.
