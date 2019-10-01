# Attendez-moi !

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

Les exemples montrent ici une utilisation directe de notre tâche au sein d'une boucle, mais nous pourrions tout aussi bien l'utiliser derrière un `await`.

```python
>>> async def runner():
...     await ComplexWork()
... 
>>> loop.run_until_complete(runner())
Hello
World
```

Il est peu fréquent d'avoir à définir un *awaitable* autre qu'une coroutine, mais cela peut être utile pour toucher aux aspects bas-niveau du moteur asynchrone ou pour associer un état à notre tâche.

L'exemple suivant présente une tâche permettant d'attendre d'avoir été notifiée pour continuer.

```python
class Waiter:
    def __init__(self):
        self.done = False

    def __await__(self):
        while not self.done:
            yield
```

Son code est relativement simple, l'objet est initialisé avec un état `done` à `False`, et l'itérateur renvoyé bouclera tant que cet état ne sera pas `True`, forçant la boucle appelante à attendre.

À l'utilisation, cela nous donne :

```python
>>> waiter = Waiter()
>>>
>>> async def wait_job(waiter):
...     print('start')
...     await waiter # wait for count_up_to to be finished
...     print('finished')
...
>>> async def count_up_to(waiter, n):
...     for i in range(n):
...         print(i)
...         await asyncio.sleep(0)
...     waiter.done = True
...
>>> loop.run_until_complete(asyncio.gather(wait_job(waiter), count_up_to(waiter, 10)))
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

Comme on le voit, notre objet `Waiter` permet à `wait_job` d'attendre la fin de l'exécution de `count_up_to` avant de continuer.
Vous pouvez d'ailleurs faire varier le temps de *sleep* pour constater que ce n'est pas un hasard et que `«ait_job` attend bien.