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

La « boucle » que nous utilisons pour le moment ne permet aucune interaction : une fois lancée, il n'est par exemple plus possible d'ajouter de nouvelles tâches. Ça limite beaucoup les cas d'utilisation.

Pour remédier à cela, nous allons donc transformer notre fonction en classe afin de lui ajouter un état (la liste des tâches en cours) et une méthode `add_task` pour programmer de nouvelles tâches à la volée.

```python
class Loop:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        if hasattr(task, '__await__'):
            task = task.__await__()
        self.tasks.append(task)

    def run(self):
        while self.tasks:
            task = self.tasks.pop(0)
            try:
                next(task)
            except StopIteration:
                pass
            else:
                self.add_task(task)
```

Les deux premières lignes de la méthode `add_task` sont utiles pour reprogrammer une tâche déjà en cours (appel ligne 18), qui aura déjà été transformée en itérateur auparavant.

On peut aussi ajouter une méthode utilitaire, `run_task`, pour faciliter le lancement d'une tâche seule.

```python
class Loop:
    [...]

    def run_task(self, task):
        self.add_task(task)
        self.run()
```

À l'utilisation, on retrouve le même comportement que précédemment.

```python
>>> loop = Loop()
>>> loop.run_task(print_messages('foo', 'bar', 'baz'))
foo
bar
baz
```

Notre boucle possède maintenant un état, mais il n'est toujours pas possible d'interagir avec elle depuis nos tâches asynchrones, car nous n'avons aucun moyen de connaître la boucle en cours d'exécution.  
Pour cela, nous ajoutons un attribut de classe `current` référençant la boucle en cous, réinitialisé à chaque `run`.

```python
class Loop:
    [...]

    current = None

    def run(self):
        Loop.current = self
        [...]
```

Dans un environnement réel, il nous faudrait réinitialiser `current` à chaque tour de boucle dans le `run`, pour permettre à plusieurs boucles de coexister.
Mais le code proposé ici ne l'est qu'à titre d'exemple, on notera aussi que le traitement n'est pas *thread-safe*.

--------------------

Cet attribut `Loop.current` va nous être d'une grande utilité pour réaliser notre propre coroutine `gather`.
Pour rappel, cet outil permet de lancer plusieurs coroutines « simultanément » et d'attendre qu'elles soient toutes terminées.

On peut commencer par reprendre notre classe `Waiter` pour étendre son comportement.
Plutôt que de n'avoir qu'un état booléen, on le remplace par un compteur, décrémenté à chaque notification.
On le dote alors d'une méthode `set` pour le notifier.
L'attente d'un objet `Waiter` se termine une fois qu'il a été notifié `n` fois.

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

À partir de ce `Waiter` il devient très facile de recoder `gather`.
Il suffit en effet d'instancier un `Waiter` en lui donnant le nombre de tâches, d'ajouter ces tâches à la boucle courante à l'aide de `Loop.current.add_task`, et d'attendre le `Waiter`.

Une petite subtilité seulement : les tâches devront être enrobées dans une nouvelle coroutine afin qu'elles notifient le `Waiter` en fin de traitement.

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

On constate bien l'exécution concurrente des tâches, il est possible de faire varier le temps de pause pour observer les changements.

```python
>>> loop = Loop()
>>> loop.run_task(
...     gather(
...         print_messages('foo', 'bar', 'baz'),
...         print_messages('aaa', 'bbb', 'ccc', sleep_time=0.7),
...     )
... )
foo
aaa
bbb
bar
ccc
baz
```

Et contrairement à notre précédent `run_tasks` qui permettait déjà celà, `gather` peut s'utiliser partout derrière un `await`, permettant de construire de vrais *workflows*.

```python
>>> async def workflow():
...     await gather(
...         print_messages('a', 'b'),
...         print_messages('c', 'd', 'e'),
...     )
...     await print_messages('f', 'g')
...
>>> loop.run_task(workflow())
a
c
b
d
e
f
g
```

--------------------

\+ exemple socket + socketserver (select + await release)
