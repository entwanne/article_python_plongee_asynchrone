# Quelques autres outils

Depuis les dernières versions de Python se sont développés de nouveaux outils autour de ces tâches asynchrone, afin de pouvoir profiter d'un environnement complet.

Il s'agit en fait d'ajouter un mode asynchrone à deux outils existants : la boucle `for` et le bloc `with`.
De la même manière qu'on passe de `def` à `async def` pour une fonction asynchrone (coroutine), les mot-clés `async for` et `async with` ont été introduits.

## Itérables & générateurs asynchrones

Depuis une coroutine, il est donc maintenant possible d'utiliser un `async for` pour boucler sur un itérable asynchrone.

Mais qu'est-ce donc qu'un itérable asychrone ?
C'est un itérable qui produit ces éléments asynchrones.

Un itérable en Python est défini par une méthode `__iter__` renvoyant un itérateur, lui-même défini par une méthode `__next__` renvoyant le prochain élément (ou levant une exception `StopIteration` s'il est entièrement consommé).
De façon similaire, un itérable asynchrone possède une méthode `__aiter__` renvoyant un itérateur asynchrone doté d'une méthode-coroutine `__anext__` renvoyant l'élément suivant (ou levant une exception `StopAsyncIteration`).
Le fait que cette dernière méthode soit une coroutine lui permet d'utiliser tous les outils asynchrones.

Le code suivant définit un itérable asynchrone `ARange` et son itérateur associé.

```python
class ARange:
    def __init__(self, stop):
        self.stop = stop

    def __aiter__(self):
        return ARangeIterator(self)


class ARangeIterator:
    def __init__(self, arange):
        self.arange = arange
        self.i = 0

    async def __anext__(self):
        if self.i >= self.arange.stop:
            raise StopAsyncIteration
        await sleep(1)
        i = self.i
        self.i += 1
        return i
```

```python
>>> async def test_for():
...     async for val in ARange(5):
...         print(val)
...
>>> loop = Loop()
>>> loop.run_task(test_for())
0
1
2
3
4
```

Python 3.6 a aussi apporté les générateurs asynchrones pour simplifier l'écriture de tels itérables/itérateurs, en associant les mots-clés `async def` et `yield`.

```python
async def arange(stop):
    for i in range(stop):
        await sleep(1)
        yield i
```

L'objet renvoyé par `arange` est un itérateur asynchrone et s'utilise donc de la même façon que les objets `ARange`.

\+ listes en intension + `async` ?

## Gestionnaires de contexte asynchrones

Procédé identique pour les contextes : les classiques méthodes `__enter__` et `__exit__` deviennent `__aenter__` et `__aexit__` dans la version asynchrone, utilisable depuis une coroutine avec un `async with`.

```python
class SQL:
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        await self.conn.connect()
        return self.conn

    async def __aexit__(self, *args):
        await self.conn.close()
```

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def sql():
    try:
        print('Connecting...')
        await sleep(1)
        yield
    finally:
        print('Closing')
        await sleep(1)
```

<https://www.python.org/dev/peps/pep-0492/>
