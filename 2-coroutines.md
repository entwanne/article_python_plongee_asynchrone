Les coroutines sont un cas particulier d'_awaitable_, définies à l'aide des mots-clés `async def`.

* Création d'une première coroutine
* Itération sur le générateur associé à une coroutine (__await__ + boucle for)

* Coroutine utilisant notre awaitable release
* Coroutines imbriquées
* Itération manuelle (__await__ + next())

* Coroutines et futures: await asyncio.sleep (traiter le résultat manuellement)

```python
async def my_coro():
    print('I am a coroutine')
```

Cette coroutine est une tâche asynchrone, nous pouvons itérer dessus de la même manière que précédemment.

```python
>>> for _ in producer_task().__await__():
...     pass
... 
I am a coroutine
```

Il est aussi possible de faire appel à nos autres tâches asynchroens à l'intérieur des coroutines.

```python
async def super_producer():
    print('Subtask:')
    await ProducerTask()
```

```python
>>> for _ in super_producer().__await__():
...     pass
... 
Subtask:
Hello
World!
```

Aussi, par commodité, nous renommerons `AsyncTask` en `release`, cette tâche n'ayant pour but que de rendre la main au moteur.

```python
class release:
    def __await__(self):
        yield
```

