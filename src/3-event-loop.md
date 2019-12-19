# Boucle d'or et les trois tâches

Après avoir défini différentes tâches aysnchrones, il serait intéressant de construire le moteur pour les exécuter, la boucle événementielle.
Cette boucle se charge de cadencer et d'avancer dans les tâches, tout en tenant compte des événements qui peuvent survenir.

Nous avons déjà un algorithme basique, que nous suivons pour le moment manuellement,  pour traiter une tâche :

* Faire appel à `__await__` pour récupérer l'itérateur associé.
* Appeler continuellement `next` sur cet itérateur.
* S'arrêter quand une exception `StopIteration` est levée.

Il nous est donc possible d'écrire cela sous la forme d'une fonction `run_task` prenant une unique tâche en paramètre.

```python
def run_task(task):
    it = task.__await__()

    while True:
        try:
            next(it)
        except StopIteration:
            break
```

Ce premier prototype de boucle fonctionne, nous pouvons l'utiliser pour exécuter l'une de nos tâches.

```python
>>> run_task(complex_work())
Hello
World
```

Mais il est assez limité, ne traitant pas du tout la question de l'exécution concurrente, du cadencement.
Pour l'améliorer, nous créons donc la fonction `run_tasks`, recevant une liste de tâches.
Les itérateurs de ces tâches seront placés dans une file (*FIFO*) par la boucle, qui pourra alors à chaque itération récupérer la prochaine tâche à traiter et la faire avancer d'un pas.
Après quoi, si la tâche n'est pas terminée, elle sera ajoutée en fin de file pour être continuée plus tard.

```python
def run_tasks(*tasks):
    tasks = [task.__await__() for task in tasks]

    while tasks:
        # On prend la première tâche disponible
        task = tasks.pop(0)
        try:
            next(task)
        except StopIteration:
            # La tâche est terminée
            pass
        else:
            # La tâche continue, on la remet en queue de liste
            tasks.append(task)
```

On obtient maintenant une exécution réellemment concurrente.
Le mécanisme de file (algorithme type *round-robin*) permet de traiter toutes les tâches de la même manière, sans en laisser sur le carreau.
Ce sont néanmoins les tâches qui contrôlent la cadence, choisissant explicitement quand elles rendent la main à la boucle (`yield` / `await asyncio.sleep(0)` ou équivalents), lui permettant de passer à la tâche suivante.

Pour nous assurer du bon fonctionnement, on peut tester notre fonction avec nos coroutines `wait_job` et `count_up_to`.

```python
>>> waiter = Waiter()
>>> run_tasks(wait_job(waiter), count_up_to(waiter, 10))
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
```

Cependant, un moteur asynchrone n'est rien sans les utilitaires qui vont avec.
Nous avons vu la fonction `sleep` pour *asyncio* qui permet de patienter un certain nombre de secondes, et il serait utile d'en avoir un équivalent dans notre environnement.

Vous me direz que l'on utilise déjà `await asyncio.sleep(0)` dans nos coroutines et que ça ne pose pas de problème particulier, mais c'est justement parce que le paramètre vaut 0.
Une autre valeur provoquerait une erreur parce que ne serait pas gérée par notre boucle événementielle.

Commencçons par une tâche élémentaire toute simple, qui nous servira à construire le reste.
Pour rendre la main à la boucle événementielle, il est nécessaire d'avoir un itérateur qui produit une valeur.
Mais nous ne pouvons pas le faire directement depuis nos coroutines avec un `yield`, il faut nécessairement passer par une autre tâche que l'on `await`.

Il nous serait pratique d'avoir une tâche `interrupt`, où un `await interrupt()` serait équivalent à un `yield` / `await asyncio.sleep(0)`.
C'est le cas avec la classe suivante.

```python
class interrupt:
    def __await__(self):
        yield
```

La tâche est peu utile en elle-même, mais elle permet de construire autour d'elle un environnement de coroutines.
Par exemple, on peut imaginer une coroutine qui rendrait la main à la boucle (et donc patienterait) tant qu'un temps n'a pas été atteint.

```python
import time

async def sleep_until(t):
    while time.time() < t:
        await interrupt()
```

Partant de là, une coroutine `sleep` se construit facilement en transformant une durée (temps relatif) en temps absolu.

```python
async def sleep(duration):
    await sleep_until(time.time() + duration)
```

À titre d'exemple, voici une coroutine qui affiche des messages reçus en arguments, espacés par une certaine durée.

```python
async def print_messages(*messages, sleep_time=1):
    for msg in messages:
        print(msg)
        await sleep(sleep_time)
```

On l'utilise ensuite avec `run_tasks` en instanciant deux coroutines pour bien voir que leurs messages s'intermêlent, et donc qu'il n'y a pas d'attente active : la boucle est capable de passer à la tâche suivante quand la première est bloquée, il lui suffit de rencontrer une interruption.

```python
>>> run_tasks(
...     print_messages('foo', 'bar', 'baz'),
...     print_messages('aaa', 'bbb', 'ccc', sleep_time=0.7),
... )
foo
aaa
bbb
bar
ccc
baz
```

(Le résultat n'est pas très parlant ici vu qu'il manque de dynamisme, je vous invite à l'exécuter chez vous pour mieux vous en rendre compte.)

--------------------

* Définition d'une vraie classe de boucle avec des méthodes call_soon / run / run_until_complete
* Rendre la boucle accessible dans les tâches (get_current_loop)

Mais une boucle serait plus utile si on pouvait interagir avec elle, pour programmer de nouvelles tâches par exemple.

```python
class Loop:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task.__await__())

    def run(self):
        while self.tasks:
            task = self.tasks.pop(0)
            try:
                next(task)
            except StopIteration:
                pass
            else:
                self.tasks.append(task)

    def run_task(self, task):
        self.add_task(task)
        self.run()
```

```python
>>> loop = Loop()
>>> loop.run_task(print_messages('foo', 'bar', 'baz'))
foo
bar
baz
```

On pourrait pour le moment se demander l'intérêt de cette classe.
Le tout vient de la fonction `add_task`, qui permettrait à un élément extérieur d'ajouter des tâches, si tant est qu'il ait accès à la boucle.

Nous allons pour cela considérer que nous sommes dans un environnement simple avec un seul _thread_ et utiliser une variable globale pour stocker la boucle courante.

```python
class Loop:
    current = None

    ...

    def run(self):
        Loop.current = self
        ...
```

```python
class Waiter:
    def __init__(self, n=1):
        self.i = n

    def set(self):
        self.i -= 1

    def __await__(self):
        while self.i > 0:
            yield
```

```python
async def gather(*tasks):
    waiter = Waiter(len(tasks))

    async def task_wrapper(task):
        await task
        waiter.set()

    for t in tasks:
        Loop.current.add_task(task_wrapper(t))
    await waiter
```

```python
>>> loop.run_task(gather(print_messages('foo', 'bar', 'baz'),
...     print_messages('aaa', 'bbb', 'ccc', sleep_time=0.7)))
foo
aaa
bbb
bar
ccc
baz
```

\+ exemple socket + socketserver (select + await release)
