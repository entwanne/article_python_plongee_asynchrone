# Un monde de coroutines

Depuis Python 3.5, une coroutine se définit à l'aide des mots-clés `async def` :

```python
async def simple_print(msg):
    print(msg)
```

Techniquement, `simple_print` n'est pas une coroutine.
C'est en fait une fonction qui renvoie une nouvelle coroutine à chaque appel.
Comme toute fonction, `simple_print` peut donc recevoir des arguments, qui seront utilisés par la coroutine et influeront sur son comportement.

```python
>>> simple_print
<function simple_print at 0x7f0873895950>
>>> simple_print('Hello')
<coroutine object simple_print at 0x7f08738959e0>
```

Le contenu d'une coroutine ne s'exécute pas directement, il faut la lancer dans un environnement asynchrone.
Par exemple avec un `await` utilisé depuis une autre coroutine.

Ici nous allons faire appel à `asyncio`, le moteur asynchrone de la bibliothèque standard.
Il possède une méthode `run` permettant d'exécuter le contenu d'une coroutine.

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

Il s'agit donc d'une boucle événementielle, chargée d'exécuter et de cadencer les différentes tâches.
La boucle est propre au moteur asynchrone utilisé, et permet une utilisation concurrente des tâches.

Mais de quoi est donc faite une coroutine ?
Comment fait ce `run_until_complete` pour exécuter notre code ?

En inspectant l'objet renvoyé par `simple_print`, on remarque qu'il possède une méthode `__await__`.

```python
>>> coro = simple_print('Hello')
>>> dir(coro)
['__await__', ...]
```

La coroutine serait donc un objet avec une méthode spéciale `__await__`.
Nous voilà un peu plus avancés, plus qu'à en apprendre davantage sur cette méthode.

Mais aussi que l'appel à cette méthode renvoie un itérateur.
On voit qu'elle s'appelle sans arguments et qu'elle renvoie un objet de type `coroutine_wrapper`.
Mais en inspectant à nouveau, on remarque que cet objet est un itérateur !

```python
>>> aw = coro.__await__()
>>> aw
<coroutine_wrapper object at 0x7fcde8f30710>
>>> dir(aw)
[..., '__iter__', ..., '__next__', ..., 'send', 'throw']
```

Plus précisément, il s'agit ici d'un générateur, reconnaissable aux méthodes `send` et `throw`.

En résumé, les coroutines possèdent donc une méthode `__await__` qui renvoie un itérateur.
Cela semble logique si vous vous souvenez des articles donnés en introduction, qui montrent que la coroutine est un enrobage autour d'un générateur.

Les coroutines pouvant être converties en itérateurs, on comprend maintenant comment la boucle événementielle est capable des les parcourir.
Une simple boucle `for` pourrait faire l'affaire, en itérant manuellement sur l'objet renvoyé par `__await__`.

```python
>>> for _ in simple_print('Hello').__await__():
...     pass
... 
Hello
```

La coroutine présentée ici ne réalise aucune opération asynchrone, elle ne fait qu'afficher un message.
Voici un exemple plus parlant d'une coroutine plus complexe faisant appel à d'autres tâches.

```python
async def complex_work():
    await simple_print('Hello')
    await asyncio.sleep(0)
    await simple_print('World')
```

Le comportement est le même : itérer sur l'objet renvoyé par `__await__` permet d'exécuter le corps de la coroutine.

```python
>>> for _ in complex_work().__await__():
...     pass
... 
Hello
World
```

Mais avec cette simple boucle on ne voit pas clairement ce qui délimite les itérations.
Impossible de savoir en voyant le code précédent combien la boucle a fait d'itérations (et donc à quel moment elle a repris la main).

Les itérateurs ne s'utilisent pas uniquement avec des boucles `for`, on peut aussi les parcourir pas à pas à l'aide de la fonction `next`.
`next` renvoie à chaque appel l'élément suivant de l'itérateur, et lève une exception `StopIteration` en fin de parcours.
C'est donc cette fonction que nous allons utiliser pour l'exécution, qui rendra visible chaque interruption de la tâche.

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

Cela apparaît très clairement maintenant, notre boucle réalise deux itérations.
Chaque interruption permet à la boucle de reprendre la main, de gérer les événements et de cadencer les tâches (choisir de les suspendre ou les continuer), c'est ainsi qu'elle peut en exécuter « simultanément » (de façon concourrente).

C'est ici l'expression `await asyncio.sleep(0)` qui est responsable de l'interruption dans notre itération, elle est similaire à un `yield` pour un générateur.
`await` est l'équivalent du `yield from`, il délégue l'itération à une sous-tâche.
Il ne provoque pas d'interruption en lui-même, celle-ci ne survient que si elle est déclenchée par la sous-tâche (nous verrons par la suite par quel moyen).

`asyncio.sleep(0)` est un cas particulier de `sleep` qui ne fait qu'une simple interruption, sans attente. Le comportement serait différent avec un temps non nul.
