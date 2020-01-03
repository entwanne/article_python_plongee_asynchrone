# No Future

Le moteur asynchrone du chapitre précédent est assez peu efficace, notamment sa fonction `sleep`.
En effet : la tâche est bien interrompue le temps de l'attente, mais elle est reprogrammée par la boucle à chaque itération, pour rien.
De même pour la tâche `Waiter` qui n'a normalement pas besoin d'être programmée tant que son compteur ne vaut pas zéro.

On sait qu'une tâche est suspendue car elle attend qu'une condition (temporelle ou autre) soit vraie.
il serait alors intéressant que la boucle événementielle ait connaissance de cela et ne cadence que les tâches dont les préconditions sont remplies.

Pour éviter ce problème, `asyncio` utilise un mécanisme de *futures*.
Une *future* est une tâche asynchrone spécifique, qui permet d'attendre un résultat qui n'a pas encore été calculé.
La *future* ne peut être relancée par la boucle événementielle qu'une fois ce résultat obtenu.

Il se trouve que le `yield` utilisé dans nos tâches pour rendre la main à la boucle peut s'accompagner d'une valeur, comme dans tout générateur.
Ici, il va nous servir à communiquer avec la boucle, pour lui indiquer la *future* en cours.
C'est ce que fait `asyncio.sleep` avec une durée non nulle par exemple.

On peut commencer avec un prototype de *future* tout simple, sur le modèle de notre première classe `Waiter`.

```python
class Future:
    def __await__(self):
        yield self
        assert self.done
```

Nous n'avons pas besoin de boucle ici, puisque la tâche ne devrait pas être programmée plus de deux fois : une première fois pour démarrer l'attente, et une seconde après que la condition soit remplie pour reprendre le travail de la tâche appelante.
On place néanmoins un `assert` pour s'assurer que ce soit bien le cas.

Lorsque, depuis une coroutine, on fera un `await Future()`, la valeur passée au `yield` remontera le flux des appels jusqu'à la boucle événementielle, qui la recevra en valeur de retour de `next`.
Ainsi, un `yield self` depuis la classe `Future` permettra à la boucle d'avoir accès à la *future* courante.
C'est le seul moyen pour la boucle d'y avoir accès, puisqu'elle ne possède sinon qu'une référence vers la tâche asynchrone englobante.

--------------------

Pour améliorer notre classe `Future`, on va l'agrémenter d'une méthode `set` afin de signaler que le traitement est terminé.
En plus de cela, la méthode se chargera aussi de reprogrammer notre tâche au niveau de la boucle événementielle (c'est à dire de l'ajouter à nouveau aux tâches à exécuter, afin qu'elle soit prise en compte à l'itération suivante).

Pour connaître la tâche à cadencer, on va utiliser l'attribut `task` de l'objet `Future`. Il n'existe pas encore pour le moment, mais sa valeur lui sera attribuée par la boucle événementielle lorsque la tâche sera interrompue.

```python
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
```

Notre tâche `Future` est maintenant complète, mais le reste du travail est à appliquer du côté de la boucle, pour qu'elle les traite correctement.

* Premièrement, il faut que quand une tâche s'interrompt sur une *future*, la boucle définisse l'attribut `task` de la *future* comme convenu.
* Ensuite, la boucle ne doit pas reprogrammer une telle tâche, puisque ça provoquerait un doublon lorsque la *future* serait notifiée.
* Enfin, il est nécessaire de lier les *futures* à des événements, pour que l'appel à `set` et donc le déclenchement de la tâche soient automatiques.

On commence par les deux premiers points, faciles à ajouter à la méthode `run` de `Loop`.

```python
class Loop:
    [...]

    def run(self):
        Loop.current = self
        while self.tasks:
            task = self.tasks.pop(0)
            try:
                result = next(task)
            except StopIteration:
                continue

            if isinstance(result, Future):
                result.task = task
            else:
                self.tasks.append(task)
```

Pour le troisième point, on va formaliser l'idée d'événements.
Les plus simples à mettre en place sont les événements temporels, et ce sont donc les seuls que nous allons traiter ici.
En effet, la boucle a conscience du temps qui s'écoule et peut déclencher des actions en fonction de ça.
Le but sera donc d'associer un temps à une *future*, et d'y faire appel dans la boucle.

Tout d'abord, on crée une classe `TimeEvent` associant ces deux éléments.
On rend les objets de cette classe ordonnables, en implémentant les méthodes spéciales `__eq__` (opérateur `==`) et `__lt__` (opérateur `>`) puis en appliquant le décorateur `functools.total_ordering` pour générer les méthodes des autres opérateurs.  
On a besoin que les objets soient ordonnables pour trouver facilement les prochains événements à déclencher.

```python
from functools import total_ordering

@total_ordering
class TimeEvent:
    def __init__(self, t, future):
        self.t = t
        self.future = future

    def __eq__(self, rhs):
        return self.t == rhs.t

    def __lt__(self, rhs):
        return self.t < rhs
```

On intègre les événements temporels à notre boucle en la dotant d'une méthode `call_later`.
Cette méthode reçoit un temps et une *future*, les associe dans un objet `TimeEvent` qu'elle ajoute à la file des événements.
On utilise pour la file un objet `heapq` qui permet de conserver un ensemble ordonné : le premier événement de la file sera toujours le prochain à exécuter.

`heapq` est un module fournissant des fonctions (`heappush`, `heappop`) qui s'appuient sur une liste pour garder une file cohérente.

```python
import heapq

class Loop:
    [...]

    handlers = []

    def call_later(self, t, future):
        heapq.heappush(self.handlers, TimeEvent(t, future))
```

Dans le cœur de la boucle (méthode `run`), il suffit alors de regarder l'événement en tête de file, et de le déclencher si besoin (si son temps est atteint).
Déclencher l'événement signifie notifier la *future* qui lui est associée (appeler sa méthode `set`).
L'effet sera donc immédia, la *future* ajoutera la tâche suspendue aux tâches courantes, et celle-ci sera prise en compte par la boucle pendant l'itération.
Le reste de la méthode `run` reste inchangé.

```python
class Loop:
    [...]

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
```

--------------------

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
        self.task = None

    def __await__(self):
        yield self
        assert self._done

    def set(self):
        self._done = True
        if self.task is not None:
            Loop.current.add_task(self.task)
```

```python
class Loop:
    ...

    def run(self):
        ...
        if isinstance(result, Future):
            result.task = task
        else:
            self.tasks.append(task)
```

```python
@total_ordering
class TimeEvent:
    def __init__(self, t, future):
        self.t = t
        self.future = future
    def __eq__(self, rhs):
        return self.t == rhs.t
    def __lt__(self, rhs):
        return self.t < rhs

class Loop:
    ...
    def call_later(self, t, future):
        heapq.push(self.handlers, TimeEvent(t, future))

    def run(self):
        ...
        if self.handlers and self.handlers[0].t <= time.time():
            handler = heapq.pop(self.handlers)
            handler.future.set()
        ...
```
