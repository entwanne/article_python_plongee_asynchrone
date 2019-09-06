* Création d'une première coroutine
* Lancement dans une boucle asyncio
* Itération sur le générateur associé à une coroutine (__await__ + boucle for)
* Coroutines imbriquées
* Itération manuelle (__await__ + next())

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

---

* Define coroutine with simple print (`async def simple_print(msg)`)
* + coroutine with multiple `await asyncio.sleep(0)` and await the previous one

* Run with `asyncio.run`
* Run with `loop.run_until_complete` (= asyncio.run sans les opérations de finalisation)
* Run with `for _ in aw.__await__(): print('interrupt')`
* Run manually: `gen = aw.__await__(); next(gen); ...`
