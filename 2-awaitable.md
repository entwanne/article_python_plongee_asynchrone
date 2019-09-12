On a vu que les coroutines pouvaient s'utiliser dans des boucles événementielles ou derrière le mot-clé *await*, mais d'autres objets en sont aussi capables.
On parle plus généralement de tâches asynchrones ou d'*awaitables*.

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
