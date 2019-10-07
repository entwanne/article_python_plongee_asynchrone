# Boucles événementielles

* Notion de boucle évenementielle
* Notion de rendre la main à la boucle (asyncio.sleep(0) = yield)
* Définition d'un awaitable release

* Remplacement de nos itérations manuelles par un premier prototype de boucle évenementielle (boucle for)

* Gestion parallèle de plusieurs tâches: gather

* Socket: client + serveur

* Notion de priorisation des tâches

La boucle événementielle est donc l'utilitaire chargé de cadencer et exécuter nos tâches, en tenant compte des événements extérieurs.

Avec nos précédents codes nous avons de quoi mettre en place un premier prototype de boucle événementielle, gérant une unique tâche, sous la forme d'une simple fonction.

```python
def run_task(task):
    it = task.__await__()

    while True:
        try:
            next(it)
        except StopIteration:
            break
```

Mais quel intérêt d'utiliser un modèle asynchrone pour n'exécuter qu'une seule tâche ?

L'idée serait alors d'avoir une fonction `run_tasks` recevant une liste de tâches, et les parcourant simultanément, passant à la suivante chaque fois qu'une tâche lui rend la main.

Nous pouvons pour cela procéder avec une file de tâches, en sortant une tâche à chaque itération pour la faire avancer d'un pas, et l'ajouter à nouveau à la file si elle n'est pas terminée.
La file permet à ce qu'aucune tâche ne soit laissée sur la touche.

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

Que nous pouvons utiliser comme suit :

```python
>>> run_tasks(simple_print(1), ComplexWork(), simple_print(2), simple_print(3))
1
Hello
2
3
World
```

Ou avec notre objet `Waiter` :

```python
>>> waiter = Waiter()
>>> run_tasks(wait_job(waiter), count_up_to(waiter, 5))
start
0
1
2
3
4
finished
```

(Attention toutefois dans ce cas à bien utiliser un `asyncio.sleep(0)` dans `count_up_to`, nous verrons plus loin pourquoi notre code ne peut fonctionner avec d'autres valeurs.)

Comme on le voit dans ces deux exemples, la boucle n'attend pas qu'une tâche soit terminée avant d'exécuter les autres.
Il suffit d'une interruption dans la tâche pour que la boucle reprenne le contrôle et itère sur la suivante.

D'ailleurs, pour simplifier les exemples qui suivront, nous allons réaliser une tâche qui ne consistera qu'en une interruption.
Il sera alors facile de l'`await` depuis n'importe quelle coroutine pour renvoyer à la boucle.

```python
class interrupt:
    def __await__(self):
        yield
```

Maintenant nous pouvons utiliser cette tâche pour une coroutine qui nous sera un peu plus utile : attendre un certain temps avant de reprendre l'exécution.

Une version naïve consisterait à boucler et interrompre la tâche tant que le temps n'est pas atteint.
Nous utiliseront deux coroutines : `sleep_until` pour attendre jusqu'à un temps absolu et `sleep` pour attendre un certain nombre de secondes.

```python
import time

async def sleep_until(t):
    while time.time() < t:
        await interrupt()

async def sleep(duration):
    await sleep_until(time.time() + duration)
```

Et une simple coroutine qui nous sera utile pour nos tests :

```python
async def print_messages(*messages, sleep_time=1):
    for msg in messages:
        print(msg)
        await sleep(sleep_time)
```

Voyons maintenant ce que cela peut donner à l'exécution. Je vous laisse essayer de votre côté pour vous rendre compte de la temporisation.

```python
>>> run_tasks(print_messages('foo', 'bar', 'baz'),
...     print_messages('aaa', 'bbb', 'ccc', sleep_time=0.7))
foo
aaa
bbb
bar
ccc
baz
```

* Définition d'une vraie classe de boucle avec des méthodes call_soon / run / run_until_complete
* Rendre la boucle accessible dans les tâches (get_current_loop)

Un autre utilitaire serait une tâche permettant d'en attendre d'autres en les exécutant simultanément (l'équivalent d'une sous-boucle) qu'on appellera `gather`.

```python
def gather(*tasks)
```
