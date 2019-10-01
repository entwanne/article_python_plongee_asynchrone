# Un monde de coroutines

Depuis Python 3.5, une coroutine se définit à l'aide des mots-clés `async def` :

```python
async def simple_print(msg):
    print(msg)
```

`simple_print` est en fait ici une fonction qui renvoie une nouvelle coroutine à chaque appel.

```python
>>> simple_print
<function simple_print at 0x7f0873895950>
>>> simple_print('Hello')
<coroutine object simple_print at 0x7f08738959e0>
```

Le contenu d'une coroutine ne s'exécute pas directement, il faut que celle-ci soit lancée dans un moteur asynchrone, tel qu'`asyncio`.

```python
>>> import asyncio
>>> asyncio.run(simple_print('Hello'))
Hello
```

Derrière cette simple ligne, `asyncio` se charge d'instancier une nouvelle boucle événementielle, de démarrer notre coroutine et d'attendre que celle-ci se termine.
Si l'on omet les opérations de finalisation qu'ajoute `asyncio.run`, le code précédent est équivalent à :

```python
>>> loop = asyncio.new_event_loop()
>>> loop.run_until_complete(simple_print('Hello'))
Hello
```

Il s'agit donc d'une boucle événementielle, chargée d'exécuter et de cadencer les différentes tâches, pour permettre une utilisation concurrente.

Mais que fait donc ce `run_until_complete` pour exécuter notre code, et à quoi au juste correspond une coroutine ?
En inspectant l'objet renvoyé par `simple_print`, on remarque qu'il possède une méthode `__await__`.
Mais aussi que l'appel à cette méthode renvoie un itérateur.

```python
>>> coro = simple_print('Hello')
>>> dir(coro)
['__await__', ...]
>>> aw = coro.__await__()
>>> aw
<coroutine_wrapper object at 0x7fcde8f30710>
>>> dir(aw)
[..., '__iter__', ..., '__next__', ..., 'close', 'send', 'throw']
```

C'est en fait cet itérateur spécial qui est ensuite parcouru par la boucle événementielle.

Cela signifie que l'on pourrait donc traiter nos coroutines en itérant manuellement sur l'itérateur qu'elles renvoient.

```python
>>> for _ in simple_print('Hello').__await__():
...     pass
... 
Hello
```

Cela fonctionne aussi avec des exemples plus complexes.

```python
async def complex_work():
    await simple_print('Hello')
    await asyncio.sleep(0)
    await simple_print('World')
```

```python
>>> for _ in complex_work().__await__():
...     pass
... 
Hello
World
```

On ne le voit pas directement ici mais notre boucle parcourt bien plusieurs itérations :

```python
>>> it = complex_work().__await__()
>>> next(it)
Hello
>>> next(it)
World
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

C'est en fait le `await asyncio.sleep(0)` qui a pour effet de rendre la main à la boucle événementielle (et donc d'enclancher une nouvelle itération), il est équivalent à un `yield` dans le contexte d'un générateur (mais de manière générale `await` est plutôt équivalent à un `yield from`).

Ainsi, à chacune de ces interruptions, la boucle évenementielle reprend le contrôle et décide de suspendre ou continuer telle ou telle tâche (c'est ce qui lui permet d'en exécuter plusieurs simultanément).
