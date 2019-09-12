* Objets qui peuvent être utilisés après un `await` pour être attendus par une autre tâche asynchrone (ou être exécutés dans une boucle évenementielle)
* Méthode spéciale `__await__` qui renvoie un itérateur

* Implémentation d'awaitables simples (release + producers)
* Itération sur une tâche asynchrone (`for _ in aw.__await__(): ...`)
* Liaison avec les générateurs (utilisation d'un `yield from` dans une méthode `__await__`)
* Coroutine utilisant notre awaitable release
* Coroutines et futures: await asyncio.sleep (traiter le résultat manuellement)

---

* Define an equivalent of previous coroutine (print messages and yield)
* Show that it has the same behaviour in asyncio loops & for
* Awaitable = tâche asynchrone

* Show that we can use or new object in an `await` expression
* Example with `yield from aw.__await__()` to show messages from `simple_print` coroutine

* `asyncio.sleep` with arg>0 that returns a future (handle manually the result to continue the iteration)

On a vu que les coroutines pouvaient s'utiliser dans des boucles événementielles ou derrière le mot-clé *await*, mais d'autres objets en sont aussi capables.
On parle plus généralement de tâches asynchrones ou d'*awaitables*.

Un *awaitable* est un objet qui possède une méthode spéciale `__await__`, renvoyant un itérateur.

Voici par exemple un équivalent de notre fonction `complex_work`.

```python
class ComplexWork:
    def __await__(self):
        print('Hello')
        yield
        print('World')
```

Avec le mot-clé `yield`, notre méthode `__await__` devient une fonction génératrice et renvoie donc un itérateur.

Nous pouvons exécuter notre tâche asynchrone dans une boucle évenementielle `asyncio` :

```python
>>> loop.run_until_complete(ComplexWork())
Hello
World
```

Ou via une itération manuelle comme précédemment :

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
