* Objets qui peuvent être utilisés après un `await` pour être attendus par une autre tâche asynchrone (ou être exécutés dans une boucle évenementielle)
* Méthode spéciale `__await__` qui renvoie un itérateur

* Implémentation d'awaitables simples (release + producers)
* Itération sur une tâche asynchrone (`for _ in aw.__await__(): ...`)
* Liaison avec les générateurs (utilisation d'un `yield from` dans une méthode `__await__`)

Une tâche asynchrone est appelée un _awaitable_, c'est à dire un objet que l'on peut attendre avec le mot-clé `await` ou exécuter dans une boucle évenementielle.

Un objet est dit _awaitable_ s'il possède une méthode `__await__` renvoyant un itérateur.
Les instances de la classe `AsyncTask` suivante sont ainsi des tâches asynchrones :

```python
class AsyncTask:
    def __await__(self):
        return iter([])
```

Ou plus simplement, les générateurs étant des itérateurs :

```python
class AsyncTask:
    def __await__(self):
        yield
```

On peut voir que notre tâche s'exécute correctement dans une boucle `asyncio`.

```python
>>> import asyncio
>>> loop = asyncio.get_event_loop()
>>> loop.run_until_complete(AsyncTask())
```

Bon ce n'est pas très parlant ici parce que notre tâche ne fait rien, essayons avec une autre.

```python
class ProducerTask:
    def __await__(self):
        print('Hello')
        yield
        print('World!')
```

Et maintenant :

```python
>>> loop.run_until_complete(ProducerTask())
Hello
World!
```

La boucle `asyncio` déroule donc notre itérateur comme nous aurions pu le faire avec une boucle `for`.

```python
>>> for _ in ProducerTask().__await__():
...     pass
... 
Hello
World!
```

C'est d'ailleurs tout le principe de ces tâches : les `yield` servent d'interruptions pour rendre la main au moteur asynchrone qui peut alors se permettre de cadencer les différentes tâches tout en gérant les événements extérieurs.

Les _awaitables_ ne sont alors que des sortes de générateurs, gérés par le moteur asynchrone.
Le mot-clé `await` est d'ailleurs équivalent du `yield from` dans le contexte des tâches asynchrones.
