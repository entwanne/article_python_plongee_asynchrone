# Futures

* Point sur les futures: traiter le résultat d'un asyncio.sleep
* Réécriture de la boucle événementielle avec futures & events

Notre implémentation actuelle du `sleep` est assez inefficace : la coroutine est appelée à chaque itération alors que le temps n'est pas écoulé.
Il en est de même pour la tâche `Waiter` qui n'a normalement pas besoin d'être programmée tant que son compteur n'est pas terminé.

C'est là qu'interviennent les _futures_, permettant à la boucle de programmer les tâches quand des conditions sont atteintes.

```python
>>> async def test():
...     await asyncio.sleep(1)
...
>>> loop = Loop()
>>> loop.run_task(test())
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "defs.py", line 116, in run_task
    self.run()
  File "defs.py", line 108, in run
    next(task)
  File "<stdin>", line 2, in test
  File "/usr/lib/python3.7/asyncio/tasks.py", line 595, in sleep
    return await future
RuntimeError: await wasn't used with future
```

Le `yield` utilisé dans les _awaitables_ peut renvoyer une valeur (plutôt que `None`) qui pourra être utilisée par la boucle.

```python
class Future:
    def __await__(self):
        yield self
        assert self.done
```

La tâche s'arrêtant sur une future sera mise en pause par la boucle et réactivée seulement quand la condition de la future aura été remplie (l'assertion est là pour s'en assurer).
La future est un _awaitable_, ce qui lui permet d'être utilisée de façon transparente depuis les autres tâches.

\+ mécanisme de la boucle pour ne reprendre la coroutine ayant lancé le future que quand sa condition est remplie (programme la tâche lorsque le résultat est setté)
exemple d'une gestion d'événements temporels qui déclenchent des futures (sleep)
(liste ordonnée des futures temporelles et activation de la première antérieure au temps présent)

\+ call_later ?

```python
class Future:
    def __init__(self):
        self._done = False
        self.callback = None

    def __await__(self):
        yield self
        assert self._done

    def set(self):
        self._done = True
        if self.callback is not None:
            self.callback()
```

```python
class Loop:
    ...

    def run(self):
    ...
    if isinstance(result, Future):
        result.callback = partial(self.tasks.append, task)
    else:
        self.tasks.append(task)
```
