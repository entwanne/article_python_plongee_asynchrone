# Et pour quelques outils de plus

`async def` et `await` ne sont pas les seuls mot-clés introduits par la version 3.5 de Python.
Deux nouveaux blocs ont aussi été ajoutés : les boucles asynchrones (`async for`) et les gestionnaires de contexte asynchrones (`async with`).

Ils sont similaires à leurs équivalents synchrones mais utilisent des méthodes spéciales qui font appel à des coroutines.
Et ils ne sont utilisables qu'au sein de coroutines (de la même manière qu'`await`).

Aussi, Python n'a pas arrêté d'évoluer après cette version 3.5, et de nouveaux outils pour la programmation asynchrones sont venus s'y ajouter depuis.

## Itérables & générateurs asynchrones

### Itérables asynchrones

Pour rappel, un itérable est un objet possédant une méthode `__iter__` renvoyant un itérateur.
Et un itérateur est un objet possédant une méthode `__next__` qui renvoie le prochain élément à chaque appel.
Plus d'informations à ce sujet [ici](https://zestedesavoir.com/tutoriels/954/notions-de-python-avancees/1-starters/2-iterables/).

Sur ce même modèle, un itérable asynchrone est un objet doté d'une méthode `__aiter__` qui renvoie un itérateur asynchrone (`__aiter__` est une méthode synchrone).  
Et un itérateur asynchrone possède une méthode-coroutine `__anext__`, renvoyant le prochain élément et pouvant user de tous les outils asynchrones.

Un itérateur synchrone se termine quand sa méthode `__next__` lève une exception `StopIteration`.
Dans le cas des itérateurs asynchrones, c'est une exception `AsyncStopIteration` qui sera levée.

La boucle `async for` parcourant l'itérateur sera suspendue pendant les attentes (rendant la main à la boucle événementielle).

Le code qui suit présente la classe `ARange`, un itérable asynchrone qui produit des nombres à la manière de `range`, mais en se synchronisant sur un événement extérieur (ici un `sleep(1)`).
`ARange` représente l'itérable et `ArangeIterator` l'itérateur associé (qui n'a jamais besoin d'être utilisé directement).
`ARange` en elle-même n'a rien d'asynchrone, tout le code asynchrone se trouve dans la classe de l'itérateur.

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

Pour tester l'itérable dans notre environnement, définissons une simple coroutine utilisant un `async for` :

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

### Générateurs asynchrones

Les choses se simplifient en Python 3.6 où il devient possible de définir des générateurs asynchrones.
Il suffit d'un `yield` utilisé dans une coroutine pour la transformer en fonction génératrice asynchrone.

```python
async def arange(stop):
    for i in range(stop):
        await sleep(1)
        yield i
```

`arange` s'utilise exactement de la même manière que la classe `ARange` précédente (remplacez `ARange(5)` par `arange(5)` dans l'exemple plus haut pour le vérifier), mais avec un code bien plus court.

En Python 3.6 la syntaxe `async for` devient aussi utilisable dans les listes / générateurs / ensembles / dictionnaires en intension, toujours depuis une coroutine.

```python
>>> async def test_for():
...     print([x async for x in arange(5)])
...
>>> loop = Loop()
>>> loop.run_task(test_for())
[0, 1, 2, 3, 4]
```

## Gestionnaires de contexte asynchrones

Un gestionnaire de contexte est défini par ses méthodes `__enter__` et `__exit__` permettant d'exécuter du code en entrée et en sortie de bloc `with` (voir [ici](https://zestedesavoir.com/tutoriels/954/notions-de-python-avancees/3-further/2-context-managers/)).

Le gestionnaire de contexte asynchrone est défini sur le même modèle, avec des coroutines `__aenter__` et `__aexit__`.
Elles sont donc exécutées respectivement à l'entrée et à la sortie du bloc `async with`, utilisé dans une coroutine.

Par exemple, voici un gestionnaire de contexte permettant de créer un serveur autour de l'objet `aiosocket` que nous avons utilisé au chapitre 3.
La coroutine `__aenter__` se charge de démarrer le serveur (*bind* et *listen*), et `__aexit__` le clôt (*close*).

```python
class Server:
    def __init__(self, addr):
        self.socket = aiosocket()
        self.addr = addr

    async def __aenter__(self):
        await self.socket.bind(self.addr)
        await self.socket.listen()
        return self.socket

    async def __aexit__(self, *args):
        self.socket.close()
```

Encore une fois, nous définissons une coroutine pour pouvoir tester notre objet.
On reprend le même principe que précédemment d'un serveur qui renvoie juste l'inverse du message reçu.
Et l'on réutilise `client_coro` pour jouer le rôle du client.

```python
>>> async def test_with():
...     async with Server(('localhost', 8080)) as server:
...         with await server.accept() as client:
...             msg = await client.recv(1024)
...             print('Received from client', msg)
...             await client.send(msg[::-1])
...
>>> loop = Loop()
>>> loop.run_task(gather(test_with(), client_coro()))
Received from client b'Hello World!'
Received from server b'!dlroW olleH'
```

Cette fois-ci c'est Python 3.7 qui est venu simplifié les choses, en ajoutant le support des gestionnaires de contexte asynchrones à la `contextlib`.
Ainsi, il devient possible d'utiliser un décorateur `asynccontextmanager` pour transformer un générateur asynchrone en gestionnaire de contexte asynchrone.
L'instruction `yield` permet de séparer le code d'initialisation de celui de fermeture du bloc `async with`.

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def server(addr):
    socket = aiosocket()
    try:
        await socket.bind(addr)
        await socket.listen()
        yield socket
    finally:
        socket.close()
```

`server` s'utilise de la même manière que la classe `Server` précédente.
