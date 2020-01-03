# Attendez-moi !

## À la découverte des tâches asynchrones

Les coroutines ne sont pas les seuls objets qui peuvent s'utiliser derrière le mot-clé `await`.
Plus généralement on parle de tâches asynchrones (ou *awaitables*) pour qualifier ces objets.

Ainsi, un *awaitable* est un objet caractérisé par une méthode `__await__` renvoyant un itérateur.
Les coroutines sont un cas particulier de tâches asynchrones construites autour d'un générateur (avant Python 3.5, on créait d'ailleurs une coroutine à l'aide d'un décorateur -- `asyncio.coroutine` -- appliqué à une fonction génératrice).

Voici par exemple un équivalent à notre fonction `complex_work`.
`ComplexWork` est ici une classe dont les instances sont des tâches asynchrones.

```python
class ComplexWork:
    def __await__(self):
        print('Hello')
        yield
        print('World')
```

Avec le mot-clé `yield`, notre méthode `__await__` devient une fonction génératrice et renvoie donc un itérateur.
On utilise `yield` sans paramètre, notre boucle événementielle ne s'occupant pas des valeurs renvoyées lors de l'itération, seule l'exécution importe.

Nous pouvons exécuter notre tâche asynchrone dans une boucle évenementielle *asyncio* :

```python
>>> loop.run_until_complete(ComplexWork())
Hello
World
```

Et notre objet respecte le protocole établi : il est possible d'itérer sur le retour d'`__await__`.

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

## Synchronisation entre tâches

En pratique, il est assez peu fréquent d'avoir besoin de définir un *awaitable* autre qu'une coroutine.
C'est néanmoins utile si l'on souhaite conserver un état associé à notre tâche, pour pouvoir interagir avec elle depuis l'extérieur en altérant cet état.

Prenons par exemple la classe `Waiter` qui suit, qui permet d'attendre un résultat.

```python
class Waiter:
    def __init__(self):
        self.done = False

    def __await__(self):
        while not self.done:
            yield
```

Le principe est relativement simple : l'objet est initialisé avec un état booléen `done` à `False`, puis son générateur rend la main continuellement tant que l'état ne vaut pas `True`, forçant la boucle appelante à attendre.
Une fois cet état passe à `True`, le générateur prend fin et la tâche asynchrone est donc terminée.

On utilise `Waiter` pour synchroniser deux tâches asynchrones.
En effet, avec un objet `waiter` partagé entre deux tâches, une première peut attendre sur cet objet tandis qu'une seconde exécute un calcul avant de changer l'état du `waiter` (signalant que le calcul est terminé et permettant à la première tâche de continuer).

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

`Waiter` permet donc ici à `wait_job` d'attendre la fin de l'exécution de `count_up_to` avant de continuer.
Il est possible de faire varier le temps de `sleep` pour constater qu'il ne s'agit pas d'un hasard : la première tâche se met en pause tant que la seconde n'a pas terminé son traitement.

`gather` est un utilitaire d'*asyncio* servant à exécuter « simultanément » (en concurrence) plusieurs tâches asynchrones dans la boucle événementielle.
La fonction renvoie la liste des résultats des sous-tâches (le `[None, None]` que l'on voit dans la fin de l'exemple, nos tâches ne renvoyant rien).

D'autres utilisations de `Waiter` sont possibles, à des fins de synchronisation, par exemple pour gérer des verrous (*mutex*) entre plusieurs tâches.
